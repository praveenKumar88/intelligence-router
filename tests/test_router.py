import copy
import json
from pathlib import Path
import unittest
from router import select

ROOT = Path(__file__).resolve().parents[1]


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.task = json.loads((ROOT / "examples/task.json").read_text())
        self.evidence = json.loads((ROOT / "examples/benchmarks.synthetic.json").read_text())

    def test_cheapest_feasible_wins(self):
        result = select(self.task, self.evidence)
        self.assertEqual(result["benchmark_id"], "balanced")
        self.assertEqual(result["status"], "synthetic_demo")

    def test_unknown_task_does_not_borrow_evidence(self):
        self.task["task_family"] = "security_review"
        self.assertEqual(select(self.task, self.evidence)["status"], "needs_evaluation")

    def test_every_constraint_is_enforced(self):
        for key, value in [("min_quality", 1), ("min_reliability", 1), ("max_latency_p95_ms", 0), ("required_tools", ["test_runner"])]:
            task = copy.deepcopy(self.task)
            task["requirements"][key] = value
            self.assertEqual(select(task, self.evidence)["status"], "needs_evaluation")

    def test_invalid_numbers_rejected(self):
        for value in [float("nan"), -1, 2, True]:
            self.task["requirements"]["min_quality"] = value
            with self.assertRaises(ValueError):
                select(self.task, self.evidence)
