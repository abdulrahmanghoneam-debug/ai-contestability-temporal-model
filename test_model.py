"""Meaningful boundary, reachability, metamorphic and certificate tests."""
import itertools
import unittest
from dataclasses import replace

from model import Scenario, characterize, model_check, verify_witness


class TransitionTests(unittest.TestCase):
    def compare(self, c):
        actual, formula = model_check(c), characterize(c)
        self.assertEqual(actual["reachable"], formula["reachable"], c)
        self.assertEqual(actual["earliest_correction"], formula["earliest_correction"], c)
        return actual

    def test_certificate_replay(self):
        c = Scenario(notice=1, access_delay=1, evidence_delay=2, retention=1,
                     preservation_available=True, preservation_delay=1, budget=4)
        self.assertFalse(self.compare(c)["reachable"])
        c = replace(c, retention=2)
        result = model_check(c, witness=True)
        self.assertTrue(result["reachable"])
        verify_witness(c, result)

    def test_inclusive_retention_boundary_and_irreversible_loss(self):
        c = Scenario(notice=0, access_delay=1, evidence_delay=2, retention=3)
        self.assertTrue(self.compare(c)["reachable"])
        self.assertFalse(self.compare(replace(c, retention=2))["reachable"])

    def test_preservation_must_finish_before_loss_and_be_affordable(self):
        c = Scenario(notice=2, access_delay=1, evidence_delay=3, retention=3,
                     preservation_available=True, budget=4)
        self.assertTrue(self.compare(c)["reachable"])
        self.assertFalse(self.compare(replace(c, budget=3))["reachable"])
        self.assertFalse(self.compare(replace(c, preservation_delay=2))["reachable"])

    def test_protective_filing_does_not_restore_missing_evidence(self):
        c = Scenario(notice=2, access_delay=3, evidence_delay=2, retention=8,
                     protective_filing=True)
        self.assertTrue(self.compare(c)["reachable"])
        self.assertFalse(self.compare(replace(c, protective_filing=False))["reachable"])
        self.assertFalse(self.compare(replace(c, retention=7))["reachable"])

    def test_informative_notice_reorders_requests_without_new_evidence(self):
        c = Scenario(notice=2, access_delay=3, evidence_delay=2, retention=8)
        self.assertFalse(self.compare(c)["reachable"])
        self.assertTrue(self.compare(replace(c, informative_notice=True))["reachable"])

    def test_no_correction_without_authority_or_supported_target_error(self):
        c = Scenario(notice=0, access_delay=1, evidence_delay=1, retention=10)
        self.assertTrue(self.compare(c)["reachable"])
        self.assertFalse(self.compare(replace(c, review_authorized=False))["reachable"])
        self.assertFalse(self.compare(replace(c, target_error=False))["reachable"])

    def test_notice_based_deadline_does_not_cancel_latency_amplification(self):
        c = Scenario(notice=2, access_delay=3, evidence_delay=1, retention=20,
                     deadline_from_notice=True, filing_window=6, horizon=20)
        later = replace(c, notice=3)
        x, y = characterize(c), characterize(later)
        self.assertEqual(y["earliest_evidence"] - x["earliest_evidence"], 2)
        self.assertEqual(y["deadline"] - x["deadline"], 1)
        self.assertTrue(self.compare(c)["reachable"])
        self.assertFalse(self.compare(replace(later, filing_window=5))["reachable"])

    def test_horizon_is_separate_from_filing_deadline(self):
        c = Scenario(notice=0, access_delay=1, evidence_delay=1, retention=9,
                     filing_window=5, horizon=3, review_delay=2)
        self.assertFalse(self.compare(c)["reachable"])
        self.assertTrue(self.compare(replace(c, horizon=4))["reachable"])

    def test_boundary_exhaustion(self):
        # Independent edge domain includes late notice, insufficient budgets,
        # short horizons, both protocols and queue regimes.
        for n, a, e, r, b, i, p, f, lam in itertools.product(
                [0, 2], [1, 2], [1, 2], [0, 3], [2, 4],
                [False, True], [False, True], [False, True], [0, 1]):
            c = Scenario(notice=n, access_delay=a, evidence_delay=e, retention=r,
                         budget=b, informative_notice=i, preservation_available=p,
                         protective_filing=f, late_penalty=lam, late_after=1,
                         filing_window=3, grace=2, horizon=6, review_delay=1)
            self.compare(c)

    def test_reject_invalid_assumptions(self):
        for c in [Scenario(late_penalty=-1), Scenario(access_delay=0), Scenario(budget=2.5)]:
            with self.assertRaises(ValueError):
                model_check(c)


if __name__ == "__main__":
    unittest.main(verbosity=2)
