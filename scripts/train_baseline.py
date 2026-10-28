"""Train on train, select by dev macro F1, then evaluate the selected model on test."""
import argparse
import hashlib
import json
from pathlib import Path
import platform

import joblib
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
LABELS = ['small_model', 'big_model']


def read_splits(data, manifest):
    splits = {}
    seen = set()
    for name in ['train', 'dev', 'test']:
        raw = (data / f'{name}.jsonl').read_bytes()
        if hashlib.sha256(raw).hexdigest() != manifest['splits'][name]['sha256']:
            raise ValueError(f'{name} checksum differs from dataset audit')
        records = [json.loads(line) for line in raw.decode().splitlines()]
        if not records:
            raise ValueError(f'Empty {name} split')
        for row in records:
            if set(row) != {'id', 'prompt', 'label'} or row['label'] not in LABELS:
                raise ValueError('Invalid training row')
            if row['id'] in seen:
                raise ValueError('Duplicate ID within/across splits')
            seen.add(row['id'])
        splits[name] = records
    return splits


def make_model(c, balanced):
    return Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
        ('classifier', LogisticRegression(C=c, class_weight='balanced' if balanced else None,
                                          solver='liblinear', max_iter=2000, random_state=42))])


def metrics(actual, predicted):
    return {'accuracy': accuracy_score(actual, predicted),
            'macro_f1': f1_score(actual, predicted, labels=LABELS, average='macro', zero_division=0),
            'per_class': classification_report(actual, predicted, labels=LABELS, output_dict=True, zero_division=0),
            'confusion_matrix': confusion_matrix(actual, predicted, labels=LABELS).tolist()}


def train(data, manifest_path, reports, models):
    manifest = json.loads(manifest_path.read_text())
    splits = read_splits(data, manifest)
    xtrain = [r['prompt'] for r in splits['train']]
    ytrain = [r['label'] for r in splits['train']]
    xdev = [r['prompt'] for r in splits['dev']]
    ydev = [r['label'] for r in splits['dev']]
    trials = []
    winner = None
    best = -1
    # Prespecified grid and deterministic tie-breaking: first maximum wins.
    for c in [0.1, 1.0, 10.0]:
        for balanced in [False, True]:
            model = make_model(c, balanced)
            model.fit(xtrain, ytrain)
            score = metrics(ydev, model.predict(xdev))
            trials.append({'C': c, 'balanced': balanced, 'dev_accuracy': score['accuracy'], 'dev_macro_f1': score['macro_f1']})
            if score['macro_f1'] > best:
                winner, chosen, best = model, trials[-1], score['macro_f1']
    # No refit on dev and no test-based tuning.
    xtest = [r['prompt'] for r in splits['test']]
    ytest = [r['label'] for r in splits['test']]
    predictions = winner.predict(xtest)
    evaluation = {'selected_router': metrics(ytest, predictions),
                  'always_big': metrics(ytest, ['big_model'] * len(ytest)),
                  'always_small': metrics(ytest, ['small_model'] * len(ytest))}
    models.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    artifact = models / 'baseline.joblib'
    joblib.dump(winner, artifact)
    result = {'dataset_revision': manifest['revision'], 'split_sha256': {k:v['sha256'] for k,v in manifest['splits'].items()},
              'python': platform.python_version(), 'sklearn': sklearn.__version__, 'seed':42,
              'selection_metric': 'dev macro F1', 'trials':trials, 'selected':chosen,
              'test_examples':len(ytest), 'label_order':LABELS, 'evaluation':evaluation,
              'artifact_sha256':hashlib.sha256(artifact.read_bytes()).hexdigest(),
              'interpretation':'Agreement with rule-based labels, not downstream answer correctness or demonstrated cost savings.'}
    (reports / 'baseline-evaluation.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    lines = ['# CPU routing baseline', '',
             'TF-IDF word unigrams/bigrams + logistic regression. Features and model fit on train only. '
             'Six prespecified configurations are compared on development macro F1; ties use the first configuration. '
             'Only the selected router is evaluated on the held-out test split. No refit on development examples.', '',
             f'Selected: C={chosen["C"]}, balanced={chosen["balanced"]}; dev macro F1={best:.3f}.', '',
             '| Test policy | Accuracy | Macro F1 |', '|---|---:|---:|']
    for name, score in evaluation.items():
        lines.append(f'| {name} | {score["accuracy"]:.1%} | {score["macro_f1"]:.3f} |')
    score = evaluation['selected_router']
    lines += ['', '| Label | Precision | Recall | F1 | Support |', '|---|---:|---:|---:|---:|']
    for label in LABELS:
        s = score['per_class'][label]
        lines.append(f'| {label} | {s["precision"]:.3f} | {s["recall"]:.3f} | {s["f1-score"]:.3f} | {int(s["support"])} |')
    cm = score['confusion_matrix']
    lines += ['', '## Confusion matrix', '', 'Rows are source labels; columns are predictions.', '',
              '| Actual / predicted | Small | Big |', '|---|---:|---:|',
              f'| Small | {cm[0][0]} | {cm[0][1]} |', f'| Big | {cm[1][0]} | {cm[1][1]} |', '',
              '## Interpretation and limits', '',
              f'The test set contains {len(ytest)} prompts. These results measure agreement with heuristic annotations, '
              'not whether either downstream model produces an acceptable answer. A big-to-small disagreement is a potential '
              'under-routing error relative to that heuristic, not a verified model failure.', '',
              'No GPU or downstream model API was used. Cost savings, production latency, probability calibration, '
              'and out-of-distribution performance have not been established. Normalized exact duplicates were removed, '
              'but paraphrase leakage remains possible. Do not tune further against this test report; use dev for subsequent choices '
              'and collect a fresh independent evaluation set before production claims.', '',
              'The local model is saved at `models/baseline.joblib` (ignored by Git). Only load trusted joblib files. '
              'Reproduce using `requirements-training.txt`; full trial scores and provenance are in `baseline-evaluation.json`.']
    (reports / 'baseline-evaluation.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'selected':chosen,'test':{k:{m:v[m] for m in ['accuracy','macro_f1']} for k,v in evaluation.items()}},indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=ROOT/'data/prepared')
    parser.add_argument('--manifest', type=Path, default=ROOT/'reports/dataset-audit.json')
    parser.add_argument('--reports', type=Path, default=ROOT/'reports')
    parser.add_argument('--models', type=Path, default=ROOT/'models')
    args=parser.parse_args()
    train(args.data,args.manifest,args.reports,args.models)


if __name__ == '__main__':
    main()
