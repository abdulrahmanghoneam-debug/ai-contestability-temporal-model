import unittest
from model import Scenario
from audit_case import audit_case

class RepairTests(unittest.TestCase):
    def test_already_feasible_needs_no_added_option(self):
        r=audit_case(Scenario(notice=0,access_delay=1,evidence_delay=1,retention=10))
        self.assertEqual([x['add_options'] for x in r['inclusion_minimal_repairs']],[[]])

    def test_options_cannot_create_missing_authority(self):
        r=audit_case(Scenario(review_authorized=False))
        self.assertFalse(r['graph_check']['reachable'])
        self.assertEqual(r['inclusion_minimal_repairs'],[])

    def test_counterexample_has_three_incomparable_minimal_repairs(self):
        r=audit_case(Scenario(notice=2,access_delay=3,evidence_delay=2,retention=3,budget=4))
        observed={frozenset(x['add_options']):x['earliest_completion'] for x in r['inclusion_minimal_repairs']}
        self.assertEqual(observed,{
            frozenset(['informative_notice','preservation_available']):7,
            frozenset(['preservation_available','protective_filing']):10,
            frozenset(['preservation_available','deadline_from_notice']):10})

if __name__=='__main__':unittest.main(verbosity=2)
