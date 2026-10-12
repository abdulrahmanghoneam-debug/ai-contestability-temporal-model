"""Reproduce all synthetic tables, figures and auditable correction witnesses."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
from collections import defaultdict
from dataclasses import asdict, replace
from pathlib import Path

from model import Scenario, characterize, model_check, verify_witness

ROOT = Path(__file__).resolve().parent


def dump_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def mechanism(i, p, f):
    return "".join(letter for letter, enabled in zip("NPF", [i, p, f]) if enabled) or "Base"


def svg_bars(summary):
    order = ["Base", "N", "P", "F", "NP", "NF", "PF", "NPF"]
    by_key = {(x["mechanism"], x["deadline_origin"]): x for x in summary if x["late_penalty"] == 1}
    width, height = 1040, 550
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             '<g font-family="Arial, sans-serif" fill="#172b3a">',
             '<text x="50" y="32" font-size="23" font-weight="bold">Synthetic feasibility across 720 parameter settings per mechanism</text>',
             '<text x="50" y="58" font-size="14">Counts of reachable settings; not observed people, effect sizes, or legal compliance scores.</text>']
    left, top, bottom, chart_h = 80, 100, 420, 320
    for count in range(0, 721, 120):
        y = bottom - count / 720 * chart_h
        parts += [f'<line x1="{left}" y1="{y}" x2="1000" y2="{y}" stroke="#dbe3e8"/>',
                  f'<text x="{left-12}" y="{y+5}" text-anchor="end" font-size="13">{count}</text>']
    for j, name in enumerate(order):
        x = 110 + j * 112
        for k, origin in enumerate(["decision", "notice"]):
            count = by_key[name, origin]["reachable"]
            h = count / 720 * chart_h
            color = "#315c85" if k == 0 else "#da8d24"
            parts += [f'<rect x="{x+k*38}" y="{bottom-h}" width="32" height="{h}" fill="{color}"/>',
                      f'<text x="{x+k*38+16}" y="{bottom-h-6}" text-anchor="middle" font-size="13">{count}</text>']
        parts.append(f'<text x="{x+35}" y="446" text-anchor="middle" font-size="15">{name}</text>')
    parts += ['<rect x="80" y="475" width="17" height="17" fill="#315c85"/>',
              '<text x="105" y="489" font-size="14">Deadline measured from decision</text>',
              '<rect x="440" y="475" width="17" height="17" fill="#da8d24"/>',
              '<text x="465" y="489" font-size="14">Deadline measured from notice</text>',
              '<text x="80" y="525" font-size="14">N: informative notice | P: optional evidence preservation | F: protective filing + 3-tick supplementation</text>',
              '</g></svg>']
    (ROOT / "feasibility_counts.svg").write_text("\n".join(parts), encoding="utf-8")


def svg_frontier(rows):
    # Main grid subset; no extra outcomes invented for the illustration.
    selected = {(x["notice"], x["retention"], x["preservation_available"], x["protective_filing"]): x
                for x in rows if x["late_penalty"] == 1 and not x["deadline_from_notice"]
                and not x["informative_notice"] and x["access_delay"] == 3
                and x["evidence_delay"] == 2 and x["budget"] == 4}
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="610" viewBox="0 0 1000 610">',
             '<rect width="100%" height="100%" fill="white"/><g font-family="Arial, sans-serif" fill="#172b3a">',
             '<text x="30" y="32" font-size="22" font-weight="bold">Synthetic reachability boundaries: notice delay versus evidence retention</text>',
             '<text x="30" y="57" font-size="14">Record delay 3; base evidence delay 2; budget 4; filing deadline 6; review horizon 12.</text>']
    for j, (p, f, title) in enumerate([(False, False, "Base"), (True, False, "Preservation"),
                                      (False, True, "Protective filing"), (True, True, "Both mechanisms")]):
        x0, y0 = 95 + (j % 2)*470, 110 + (j // 2)*235
        parts.append(f'<text x="{x0}" y="{y0-18}" font-size="18" font-weight="bold">{title}</text>')
        for n in range(5):
            for r in range(2, 10):
                reachable = selected[n, r, p, f]["reachable"]
                color = "#1e766b" if reachable else "#e6e9ec"
                x, y = x0+(r-2)*39, y0+n*30
                parts.append(f'<rect x="{x}" y="{y}" width="36" height="27" fill="{color}"/>')
                parts.append(f'<text x="{x+18}" y="{y+19}" text-anchor="middle" font-size="13" fill="{"white" if reachable else "#6a7480"}">{int(reachable)}</text>')
        for n in range(5):
            parts.append(f'<text x="{x0-12}" y="{y0+n*30+19}" text-anchor="end" font-size="13">{n}</text>')
        for r in range(2, 10):
            parts.append(f'<text x="{x0+(r-2)*39+18}" y="{y0+169}" text-anchor="middle" font-size="13">{r}</text>')
        parts += [f'<text x="{x0+140}" y="{y0+190}" text-anchor="middle" font-size="13">Evidence retention tick R</text>',
                  f'<text x="{x0-50}" y="{y0+70}" transform="rotate(-90 {x0-50} {y0+70})" text-anchor="middle" font-size="13">Notice tick n</text>']
    parts += ['<text x="30" y="586" font-size="14">1 = at least one feasible correction path; 0 = no path in this finite model. All values are synthetic.</text>', '</g></svg>']
    (ROOT / "reachability_frontier.svg").write_text("\n".join(parts), encoding="utf-8")


def main():
    rows, aggregates, lookup = [], defaultdict(lambda: {"total": 0, "reachable": 0, "explored_states": 0}), {}
    mismatches = []
    grid = itertools.product(range(5), range(1, 4), range(1, 4), range(2, 10), [3, 4],
                             [False, True], [False, True], [False, True], [False, True], [0, 1, 2])
    for n, a, e, r, b, origin, info, preserve, protective, penalty in grid:
        c = Scenario(notice=n, access_delay=a, evidence_delay=e, retention=r, budget=b,
                     deadline_from_notice=origin, informative_notice=info,
                     preservation_available=preserve, protective_filing=protective, late_penalty=penalty)
        actual, derived = model_check(c), characterize(c)
        if (actual["reachable"], actual["earliest_correction"]) != (derived["reachable"], derived["earliest_correction"]):
            mismatches.append({"scenario": asdict(c), "checker": actual, "formula": derived})
        name = mechanism(info, preserve, protective)
        row = {**asdict(c), "mechanism": name, **actual,
               "earliest_record": derived["earliest_record"],
               "earliest_evidence": derived["earliest_evidence"],
               "effective_filing_deadline": c.deadline, "evidence_cutoff": c.evidence_cutoff,
               "failed_conditions": "|".join(derived["failed_conditions"])}
        rows.append(row)
        key = penalty, "notice" if origin else "decision", name
        aggregates[key]["total"] += 1
        aggregates[key]["reachable"] += int(actual["reachable"])
        aggregates[key]["explored_states"] += actual["explored_states"]
        lookup[(n, a, e, r, b, origin, info, preserve, protective, penalty)] = actual["reachable"]
    if mismatches:
        dump_json(ROOT / "mismatches.json", mismatches)
        raise AssertionError(f"{len(mismatches)} independent checker/formula disagreements")
    summary = [{"late_penalty": k[0], "deadline_origin": k[1], "mechanism": k[2], **v}
               for k, v in sorted(aggregates.items())]
    monotonic_checks, violations = 0, []
    # Each named mechanism is optional; giving an extra option cannot remove paths.
    for key, reached in lookup.items():
        for dimension in [5, 6, 7, 8]:
            if key[dimension] is False:
                improved = list(key)
                improved[dimension] = True
                monotonic_checks += 1
                if reached and not lookup[tuple(improved)]:
                    violations.append([key, improved])
    joint_rescue = []
    for origin, info in itertools.product([False, True], repeat=2):
        count, total, interaction_sum = 0, 0, 0
        for n, a, e, r, b in itertools.product(range(5), range(1, 4), range(1, 4), range(2, 10), [3, 4]):
            vals = {(p, f): lookup[n, a, e, r, b, origin, info, p, f, 1]
                    for p, f in itertools.product([False, True], repeat=2)}
            count += vals[True, True] and not vals[True, False] and not vals[False, True]
            interaction_sum += int(vals[True, True])-int(vals[True, False])-int(vals[False, True])+int(vals[False, False])
            total += 1
        joint_rescue.append({"deadline_origin": "notice" if origin else "decision", "informative_notice": info,
                            "joint_only_rescue": count, "parameter_settings": total,
                            "factorial_count_contrast": interaction_sum})
    cases = {
        "baseline_path": Scenario(notice=0, access_delay=1, evidence_delay=2, retention=3),
        "loss_blocks_protective_filing": Scenario(notice=2, access_delay=3, evidence_delay=2, retention=3,
                                                   protective_filing=True, budget=4),
        "deadline_blocks_preservation": Scenario(notice=2, access_delay=3, evidence_delay=2, retention=3,
                                                 preservation_available=True, budget=4),
        "joint_restoration": Scenario(notice=2, access_delay=3, evidence_delay=2, retention=3,
                                       preservation_available=True, protective_filing=True, budget=4),
        "notice_clock_earlier": Scenario(notice=2, access_delay=3, evidence_delay=1, retention=9,
                                         deadline_from_notice=True, filing_window=5),
        "notice_clock_later": Scenario(notice=3, access_delay=3, evidence_delay=1, retention=9,
                                       deadline_from_notice=True, filing_window=5),
    }
    witnesses = {}
    for label, c in cases.items():
        actual = model_check(c, witness=True)
        if actual["reachable"]:
            verify_witness(c, actual)
        witnesses[label] = {"scenario": asdict(c), "derived": characterize(c), "checked": actual}
    results = {
        "data_status": "Entirely synthetic exhaustive finite-domain computational experiment; no human or LLM measurements.",
        "main_grid": {"late_penalty": 1, "configurations": sum(x["late_penalty"] == 1 for x in rows)},
        "all_grid_configurations": len(rows), "formula_mismatches": len(mismatches),
        "total_explored_states_across_configurations": sum(x["explored_states"] for x in rows),
        "maximum_explored_states_in_one_configuration": max(x["explored_states"] for x in rows),
        "monotonic_option_checks": monotonic_checks, "monotonic_violations": len(violations),
        "summary": summary, "joint_rescue": joint_rescue,
        "fixed_parameters": {k: v for k, v in asdict(Scenario()).items() if k in
                             ["filing_window", "horizon", "review_delay", "preservation_delay", "late_after", "grace", "review_authorized", "target_error"]},
        "grid_values": {"notice": list(range(5)), "access_delay": [1, 2, 3], "evidence_delay": [1, 2, 3],
                        "retention": list(range(2, 10)), "budget": [3, 4], "late_penalty": [0, 1, 2],
                        "four_binary_options": ["deadline_from_notice", "informative_notice", "preservation_available", "protective_filing"]},
    }
    dump_json(ROOT / "results.json", results)
    dump_json(ROOT / "witnesses.json", witnesses)
    with (ROOT / "all_configurations.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (ROOT / "summary.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    svg_bars(summary)
    svg_frontier(rows)
    files = ["model.py", "test_model.py", "run_study.py", "all_configurations.csv", "results.json", "summary.csv",
             "witnesses.json", "feasibility_counts.svg", "reachability_frontier.svg"]
    dump_json(ROOT / "sha256_manifest.json", {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files})
    print(json.dumps({key: results[key] for key in ["all_grid_configurations", "formula_mismatches", "total_explored_states_across_configurations", "monotonic_option_checks", "monotonic_violations"]}))
    print("Main grid:")
    for row in summary:
        if row["late_penalty"] == 1:
            print(f'{row["deadline_origin"]:8} {row["mechanism"]:4} {row["reachable"]}/{row["total"]}')
    print("Joint-only restoration:", json.dumps(joint_rescue))


if __name__ == "__main__":
    main()
