"""Download, audit, deduplicate and split the pinned public routing dataset."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import unicodedata
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
REPO = 'SupraLabs/Prompt-Routing-Dataset'
REVISION = '458d9f67018a350ee84bfd5e936aeca6f2522341'
FILENAME = 'router_dataset_openai_gpt-oss-120b.jsonl'
SHA256 = '584e45e8adc9cbe77b1e86b57db84a3aa1ec48ba9d76854dbf610ead94515f49'
URL = f'https://huggingface.co/datasets/{REPO}/resolve/{REVISION}/{FILENAME}'
LABELS = {'small model': 'small_model', 'big model': 'big_model'}
FIELDS = ['prompt', 'full_answer', 'complexity_score', 'primary_domain',
          'coding_task', 'math_task', 'requires_reasoning', 'routing_choice',
          'routing_justification']


def normalized(prompt):
    # Conservative exact/format duplicate detection, not semantic deduplication.
    return ' '.join(unicodedata.normalize('NFKC', prompt).casefold().split())


def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def audit(rows):
    missing = Counter()
    invalid = []
    groups = defaultdict(list)
    mismatches = 0
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            invalid.append(i)
            continue
        absent = [k for k in FIELDS if row.get(k) is None or row.get(k) == '']
        missing.update(absent)
        valid = not absent
        valid = valid and all(isinstance(row.get(k), str) and row[k].strip()
                              for k in ['prompt', 'full_answer', 'primary_domain',
                                        'routing_choice', 'routing_justification'])
        valid = valid and type(row.get('complexity_score')) is int and 1 <= row['complexity_score'] <= 5
        valid = valid and all(type(row.get(k)) is bool for k in ['coding_task', 'math_task', 'requires_reasoning'])
        valid = valid and row.get('routing_choice') in LABELS
        if not valid:
            invalid.append(i)
            continue
        groups[normalized(row['prompt'])].append(row)
        expected = 'big model' if row['complexity_score'] >= 3 or row['coding_task'] or row['math_task'] else 'small model'
        mismatches += row['routing_choice'] != expected
    conflicts = sum(len({r['routing_choice'] for r in group}) > 1 for group in groups.values())
    return groups, dict(missing), invalid, conflicts, mismatches


def split_groups(groups, seed):
    """One representative per normalized prompt; stratify by routing label."""
    by_label = defaultdict(list)
    for key, group in groups.items():
        if len({r['routing_choice'] for r in group}) != 1:
            raise ValueError('Conflicting labels in duplicate group')
        representative = min(group, key=lambda r: r['prompt'])
        by_label[representative['routing_choice']].append({
            'id': digest(key), 'prompt': representative['prompt'],
            'label': LABELS[representative['routing_choice']]})
    splits = {name: [] for name in ['train', 'dev', 'test']}
    for label in sorted(by_label):
        ordered = sorted(by_label[label], key=lambda r: digest(f'{seed}:{r["id"]}'))
        n = len(ordered)
        n_test = int(n * .15)
        n_dev = int(n * .15)
        splits['test'].extend(ordered[:n_test])
        splits['dev'].extend(ordered[n_test:n_test+n_dev])
        splits['train'].extend(ordered[n_test+n_dev:])
    for rows in splits.values():
        rows.sort(key=lambda r: r['id'])
    return splits


def prepare(raw, output, report_dir, seed):
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise ValueError('Source SHA256 mismatch; refusing unverified dataset')
    rows = [json.loads(line) for line in raw.decode('utf-8').splitlines() if line.strip()]
    groups, missing, invalid, conflicts, mismatches = audit(rows)
    if missing or invalid or conflicts:
        raise ValueError(f'Dataset audit failed: missing={missing}, invalid_rows={invalid}, conflicting_groups={conflicts}')
    splits = split_groups(groups, seed)
    output.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for name, records in splits.items():
        payload = ''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in records).encode('utf-8')
        (output / f'{name}.jsonl').write_bytes(payload)
        hashes[name] = hashlib.sha256(payload).hexdigest()
    summary = {
        'dataset': REPO, 'revision': REVISION, 'source_url': URL,
        'source_sha256': SHA256, 'seed': seed, 'source_rows': len(rows),
        'source_label_counts': dict(sorted(Counter(r['routing_choice'] for r in rows).items())),
        'missing_fields': missing, 'invalid_rows': len(invalid),
        'exact_duplicate_rows': len(rows) - len({r['prompt'] for r in rows}),
        'normalized_duplicate_groups': sum(len(g) > 1 for g in groups.values()),
        'normalized_duplicate_rows_removed': len(rows) - len(groups),
        'conflicting_duplicate_groups': conflicts, 'rule_mismatches': mismatches,
        'splits': {name: {'rows': len(records), 'label_counts': dict(sorted(Counter(r['label'] for r in records).items())), 'sha256': hashes[name]} for name, records in splits.items()},
        'input_fields': ['prompt'], 'target_field': 'label',
        'deduplication': 'NFKC + casefold + collapsed whitespace; one representative per group',
        'limitations': ['Labels encode a heuristic, not measured candidate model success.',
                        'No semantic or near-duplicate detection; paraphrase leakage may remain.',
                        'Reference answers are unverified and are excluded from model inputs.',
                        'One public source is insufficient to establish production generalization.']}
    (report_dir / 'dataset-audit.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    lines = ['# Dataset audit', '', f'Source: [{REPO}](https://huggingface.co/datasets/{REPO}/tree/{REVISION})',
             '', f'Revision: `{REVISION}`. Seed: `{seed}`. License metadata: MIT (upstream card).', '',
             f'- Source rows: {len(rows)}', f'- Original labels: {summary["source_label_counts"]}',
             f'- Missing fields: {missing or "none"}; invalid rows: {len(invalid)}',
             f'- Exact duplicate rows: {summary["exact_duplicate_rows"]}',
             f'- Normalized duplicate rows removed: {len(rows)-len(groups)}',
             f'- Conflicting duplicate groups: {conflicts}', f'- Labels differing from the published rule: {mismatches}',
             '', '## Reproducible splits', '', '| Split | Rows | Small | Big |', '|---|---:|---:|---:|']
    for name, info in summary['splits'].items():
        lines.append(f'| {name} | {info["rows"]} | {info["label_counts"].get("small_model",0)} | {info["label_counts"].get("big_model",0)} |')
    lines += ['', 'Split each label independently: floor(15%) test, floor(15%) dev, remainder train. '
              'Sort by a seeded SHA256 of the normalized prompt ID. Deduplicate before splitting; row order does not affect membership.',
              '', '## What this can establish', '',
              'This benchmark measures reproduction of the source routing policy. Its rule sends math, coding, or complexity >= 3 to the big model. '
              'It cannot establish cost savings or downstream answer quality. The source majority-label baseline is '
              f'{max(summary["source_label_counts"].values())/len(rows):.1%}; compare classifiers against it and report per-class metrics.',
              '', 'Only `prompt` enters the classifier; `label` is the target and `id` is bookkeeping. '
              'Answers, justifications, and annotated task attributes are deliberately excluded from split files.', '',
              '## Limitations', ''] + ['- ' + x for x in summary['limitations']]
    (report_dir / 'dataset-audit.md').write_text('\n'.join(lines) + '\n')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, help='Use an existing copy (checksum is still verified)')
    parser.add_argument('--output', type=Path, default=ROOT / 'data' / 'prepared')
    parser.add_argument('--report-dir', type=Path, default=ROOT / 'reports')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    try:
        if args.source:
            raw = args.source.read_bytes()
        else:
            with urlopen(URL, timeout=60) as response:
                raw = response.read()
        result = prepare(raw, args.output, args.report_dir, args.seed)
        print(json.dumps({'source_rows': result['source_rows'], 'splits': {k: v['rows'] for k,v in result['splits'].items()}, 'report': str(args.report_dir / 'dataset-audit.md')}, indent=2))
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
