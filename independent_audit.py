"""Reproduce the independent review sample, seed 61792.

This sample was executed once during review: 1500 scenarios, 19 reachable,
no reachability or earliest-completion disagreements. Saving this script did
not repeat that run. It checks a broader parameter domain than the main grid;
it is not a proof and uses the same model definitions as the two algorithms.
All scenarios are synthetic. No human or LLM performance is measured.
"""

import json
import random
from pathlib import Path

from model import Scenario, characterize, model_check


def audit():
    rng = random.Random(61792)
    mismatches = []
    reachable = 0
    for _ in range(1500):
        # The field order is part of reproducibility: it fixes RNG consumption.
        scenario = Scenario(
            notice=rng.randrange(6),
            access_delay=rng.randrange(1, 6),
            evidence_delay=rng.randrange(1, 6),
            retention=rng.randrange(15),
            budget=rng.randrange(6),
            filing_window=rng.randrange(10),
            horizon=rng.randrange(18),
            review_delay=rng.randrange(1, 6),
            preservation_delay=rng.randrange(1, 6),
            late_after=rng.randrange(7),
            late_penalty=rng.randrange(4),
            grace=rng.randrange(6),
            deadline_from_notice=bool(rng.randrange(2)),
            informative_notice=bool(rng.randrange(2)),
            preservation_available=bool(rng.randrange(2)),
            protective_filing=bool(rng.randrange(2)),
            review_authorized=bool(rng.randrange(2)),
            target_error=bool(rng.randrange(2)),
        )
        graph_result = model_check(scenario)
        formula_result = characterize(scenario)
        reachable += graph_result["reachable"]
        graph_pair = (graph_result["reachable"], graph_result["earliest_correction"])
        formula_pair = (formula_result["reachable"], formula_result["earliest_correction"])
        if graph_pair != formula_pair:
            mismatches.append(str(scenario))
    return {"seed": 61792, "cases": 1500, "reachable": reachable, "mismatches": mismatches}


if __name__ == "__main__":
    result = audit()
    output = Path(__file__).with_name("independent_audit_results.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    if result["mismatches"]:
        raise SystemExit(1)
