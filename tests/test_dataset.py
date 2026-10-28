import tempfile
from pathlib import Path
import unittest
from scripts.prepare_dataset import audit, normalized, prepare, split_groups


def row(prompt, label='small model'):
    return dict(prompt=prompt, full_answer='reference', complexity_score=1,
                primary_domain='writing', coding_task=False, math_task=False,
                requires_reasoning=False, routing_choice=label, routing_justification='rule')


class DatasetTests(unittest.TestCase):
    def test_duplicates_cannot_cross_splits_and_order_is_irrelevant(self):
        rows = [row(f'Example {i}') for i in range(30)]
        rows += [row('  EXAMPLE   1  ')]
        groups, _, _, _, _ = audit(rows)
        splits = split_groups(groups, 42)
        reverse_groups, _, _, _, _ = audit(list(reversed(rows)))
        self.assertEqual(splits, split_groups(reverse_groups, 42))
        prompts = [normalized(r['prompt']) for records in splits.values() for r in records]
        self.assertEqual(len(prompts), 30)
        self.assertEqual(len(set(prompts)), 30)
        self.assertTrue(all(set(r) == {'id', 'prompt', 'label'} for records in splits.values() for r in records))

    def test_conflicting_labels_detected(self):
        groups, _, _, conflicts, _ = audit([row('same'), row('SAME', 'big model')])
        self.assertEqual(conflicts, 1)
        with self.assertRaises(ValueError):
            split_groups(groups, 42)

    def test_missing_and_invalid_fields_detected(self):
        bad = row('test')
        del bad['full_answer']
        wrong = row('other')
        wrong['complexity_score'] = True
        _, missing, invalid, _, _ = audit([bad, wrong])
        self.assertEqual(missing, {'full_answer': 1})
        self.assertEqual(invalid, [0, 1])

    def test_checksum_fails_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'out'
            with self.assertRaisesRegex(ValueError, 'SHA256'):
                prepare(b'changed data', out, Path(tmp) / 'reports', 42)
            self.assertFalse(out.exists())
