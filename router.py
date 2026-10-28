"""Select a configuration from task-family benchmark summaries."""
import argparse
import json
import math


def number(value, name, low=0, high=float("inf")):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f"Invalid {name}")
    return value


def select(task, evidence):
    requirements = task["requirements"]
    quality = number(requirements["min_quality"], "min_quality", high=1)
    reliability = number(requirements["min_reliability"], "min_reliability", high=1)
    latency = number(requirements["max_latency_p95_ms"], "max_latency_p95_ms")
    required_tools = requirements.get("required_tools", [])
    if not isinstance(required_tools, list) or not all(isinstance(t, str) for t in required_tools):
        raise ValueError("required_tools must be a list of strings")
    feasible = []
    for row in evidence["results"]:
        q = number(row["quality"], "quality", high=1)
        r = number(row["reliability"], "reliability", high=1)
        l = number(row["latency_p95_ms"], "latency_p95_ms")
        number(row["cost_usd_per_task"], "cost_usd_per_task")
        if row["task_family"] == task["task_family"] and q >= quality and r >= reliability and l <= latency and set(required_tools) <= set(row["execution"]["tools"]):
            feasible.append(row)
    if not feasible:
        return {"status": "needs_evaluation", "reason": "No benchmarked configuration satisfies these requirements.", "evidence_kind": evidence["kind"]}
    winner = min(feasible, key=lambda row: (row["cost_usd_per_task"], row["latency_p95_ms"], row["id"]))
    return {"status": "synthetic_demo" if evidence["kind"] == "synthetic" else "candidate", "task": task, "execution": winner["execution"], "evidence_kind": evidence["kind"], "benchmark_id": winner["id"], "metrics": {k: winner[k] for k in ("quality", "reliability", "latency_p95_ms", "cost_usd_per_task")}, "feasible_configurations": len(feasible)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task")
    parser.add_argument("--benchmarks", required=True)
    args = parser.parse_args()
    try:
        with open(args.task) as f:
            task = json.load(f)
        with open(args.benchmarks) as f:
            evidence = json.load(f)
        print(json.dumps(select(task, evidence), indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
