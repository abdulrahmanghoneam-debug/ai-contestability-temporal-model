"""Finite, synthetic timed transition model of evidence-grounded correction.

No human, LLM, employer, or legal-compliance observations are represented.
Python 3.10+, standard library only. Integer times are abstract ticks.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from heapq import heappop, heappush
from typing import NamedTuple


@dataclass(frozen=True)
class Scenario:
    notice: int = 2
    access_delay: int = 2
    evidence_delay: int = 2
    retention: int = 7
    budget: int = 3
    filing_window: int = 6
    horizon: int = 12
    review_delay: int = 2
    preservation_delay: int = 1
    late_after: int = 4
    late_penalty: int = 1
    grace: int = 3
    deadline_from_notice: bool = False
    informative_notice: bool = False
    preservation_available: bool = False
    protective_filing: bool = False
    review_authorized: bool = True
    target_error: bool = True

    def validate(self) -> None:
        for key, value in asdict(self).items():
            if isinstance(value, bool):
                continue
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"{key} must be a nonnegative integer")
        for key in ("access_delay", "evidence_delay", "review_delay", "preservation_delay"):
            if getattr(self, key) < 1:
                raise ValueError(f"{key} must be at least one tick")

    @property
    def deadline(self) -> int:
        return self.filing_window + (self.notice if self.deadline_from_notice else 0)

    @property
    def evidence_cutoff(self) -> int:
        return self.deadline + (self.grace if self.protective_filing else 0)

    def evidence_ready(self, requested_at: int) -> int:
        return (requested_at + self.evidence_delay
                + self.late_penalty * max(0, requested_at - self.late_after))


# For requested objects: -1 = not requested; -2 = collected/retained;
# evidence additionally uses -3 = irreversibly lost. Otherwise: due timestamp.
class State(NamedTuple):
    t: int = 0
    record: int = -1
    evidence: int = -1
    preservation: int = -1
    filed: int = -1
    review: int = -1
    spent: int = 0


def normalize(s: State, c: Scenario) -> State:
    """Simultaneous due events; completion at retention/deadline is inclusive."""
    t, record, evidence, preservation, filed, review, spent = s
    if record >= 0 and t >= record:
        record = -2
    if preservation >= 0 and t >= preservation:
        preservation = -2
    if evidence >= 0 and t >= evidence:
        evidence = -2 if t <= c.retention or preservation == -2 else -3
    if filed >= 0 and record == -2 and evidence == -2 and review < 0:
        if t <= c.evidence_cutoff:
            review = t + c.review_delay
    return State(t, record, evidence, preservation, filed, review, spent)


def successors(s: State, c: Scenario):
    """All permitted actions, including deliberately delayed requests."""
    if s.t < c.horizon:
        yield "wait_one_tick", normalize(s._replace(t=s.t + 1), c)
    if s.t < c.notice or s.spent >= c.budget:
        return
    spent = s.spent + 1  # all four kinds of action cost one abstract unit
    if s.record == -1:
        yield "request_record", normalize(s._replace(record=s.t + c.access_delay, spent=spent), c)
    if s.evidence == -1 and (c.informative_notice or s.record == -2):
        yield "request_evidence", normalize(s._replace(evidence=c.evidence_ready(s.t), spent=spent), c)
    if c.preservation_available and s.preservation == -1:
        if s.t + c.preservation_delay <= c.retention:
            yield "preserve_evidence", normalize(s._replace(preservation=s.t + c.preservation_delay, spent=spent), c)
    support = s.record == -2 and s.evidence == -2
    if s.filed < 0 and s.t <= c.deadline and (c.protective_filing or support):
        yield "file_request_for_review", normalize(s._replace(filed=s.t, spent=spent), c)


def is_success(s: State, c: Scenario) -> bool:
    return (c.target_error and c.review_authorized and s.review >= 0
            and s.t >= s.review and s.t <= c.horizon)


def model_check(c: Scenario, witness: bool = False) -> dict:
    """Exact reachability by enumeration; earliest target via a time-priority queue.

    Stops upon a reachable target, but explores the complete reachable state space
    when no target exists. Nothing in the closed-form theorem is used here.
    """
    c.validate()
    initial = normalize(State(), c)
    frontier = [initial]
    seen = {initial}
    predecessor = {} if witness else None
    explored = 0
    while frontier:
        s = heappop(frontier)
        explored += 1
        if is_success(s, c):
            result = {"reachable": True, "earliest_correction": s.t,
                      "explored_states": explored, "discovered_states": len(seen)}
            if witness:
                path = []
                current = s
                while current != initial:
                    previous, action = predecessor[current]
                    path.append({"action": action, "state": current._asdict()})
                    current = previous
                result["witness"] = [{"action": "initial", "state": initial._asdict()}] + path[::-1]
            return result
        for action, nxt in successors(s, c):
            if nxt not in seen:
                seen.add(nxt)
                if witness:
                    predecessor[nxt] = s, action
                heappush(frontier, nxt)
    return {"reachable": False, "earliest_correction": None,
            "explored_states": explored, "discovered_states": len(seen)}


def characterize(c: Scenario) -> dict:
    """Closed-form characterization, checked independently against the graph."""
    c.validate()
    record_at = c.notice + c.access_delay
    evidence_request = c.notice if c.informative_notice else record_at
    evidence_at = c.evidence_ready(evidence_request)
    support_at = max(record_at, evidence_at)
    preserve_possible = (c.preservation_available and c.budget >= 4
                         and c.notice + c.preservation_delay <= c.retention)
    conditions = {
        "target_error": c.target_error,
        "empowered_review": c.review_authorized,
        "base_budget": c.budget >= 3,
        "timely_notice": c.notice <= c.deadline,
        "support_before_cutoff": support_at <= c.evidence_cutoff,
        "completion_before_horizon": support_at + c.review_delay <= c.horizon,
        "evidence_survives": evidence_at <= c.retention or preserve_possible,
    }
    reachable = all(conditions.values())
    return {"reachable": reachable,
            "earliest_correction": support_at + c.review_delay if reachable else None,
            "earliest_record": record_at, "earliest_evidence_request": evidence_request,
            "earliest_evidence": evidence_at, "earliest_complete_support": support_at,
            "deadline": c.deadline, "evidence_cutoff": c.evidence_cutoff,
            "conditions": conditions,
            "failed_conditions": [name for name, ok in conditions.items() if not ok]}


def verify_witness(c: Scenario, result: dict) -> None:
    """Replay each transition; reject any certificate not licensed by the model."""
    path = result["witness"]
    assert State(**path[0]["state"]) == State()
    for left, right in zip(path, path[1:]):
        allowed = list(successors(State(**left["state"]), c))
        assert (right["action"], State(**right["state"])) in allowed
    assert is_success(State(**path[-1]["state"]), c)
