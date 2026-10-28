"""Predict the source policy label for one prompt using a trusted local model."""
import argparse
import json
from pathlib import Path
import joblib

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('prompt')
parser.add_argument('--model', type=Path, default=Path(__file__).resolve().parents[1]/'models/baseline.joblib')
args = parser.parse_args()
if not args.prompt.strip():
    parser.error('Prompt must not be empty')
model = joblib.load(args.model)
print(json.dumps({'route':str(model.predict([args.prompt])[0]), 'policy_version':'tfidf-logreg-v1', 'basis':'learned source heuristic'},indent=2))
