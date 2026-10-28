import hashlib
import json
from pathlib import Path
import tempfile
import unittest

try:
    from scripts.train_baseline import make_model, metrics, read_splits
except ModuleNotFoundError:
    make_model = None


@unittest.skipIf(make_model is None, 'Install requirements-training.txt for training tests')
class TrainingTests(unittest.TestCase):
    def test_unseen_text_does_not_change_vocabulary(self):
        model = make_model(1.0, True)
        model.fit(['poem friendly writing']*4 + ['algorithm numeric coding']*4,
                  ['small_model']*4 + ['big_model']*4)
        before = dict(model.named_steps['tfidf'].vocabulary_)
        model.predict(['unseenholdouttoken'])
        self.assertEqual(before, model.named_steps['tfidf'].vocabulary_)
        self.assertNotIn('unseenholdouttoken', before)

    def test_confusion_matrix_has_fixed_order(self):
        result = metrics(['small_model','big_model'], ['big_model','big_model'])
        self.assertEqual(result['confusion_matrix'], [[0,1],[0,1]])
        self.assertEqual(result['per_class']['small_model']['recall'], 0)

    def test_duplicate_ids_across_splits_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            manifest={'splits':{}}
            for name in ['train','dev','test']:
                raw=(json.dumps({'id':'same','prompt':'example','label':'small_model'})+'\n').encode()
                (root/f'{name}.jsonl').write_bytes(raw)
                manifest['splits'][name]={'sha256':hashlib.sha256(raw).hexdigest()}
            with self.assertRaisesRegex(ValueError,'Duplicate ID'):
                read_splits(root,manifest)
