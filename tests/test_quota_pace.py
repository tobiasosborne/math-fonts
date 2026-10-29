import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from quota_pace import evaluate


class QuotaPaceTests(unittest.TestCase):
    def setUp(self):
        self.start=datetime(2026,10,28,tzinfo=timezone.utc)
        self.reset=self.start+timedelta(days=7)
        self.snapshot={'provider_allowed':True,'windows':[{
            'kind':{'kind':'weekly'},'used':.16,'length':'PT168H',
            'resets_at':self.reset.isoformat(),'locked_reason':None}]}

    def test_behind_pace_allows_one_action(self):
        result=evaluate(self.snapshot,self.start+timedelta(days=2))
        self.assertTrue(result['allowed'])

    def test_ahead_of_pace_waits_even_inside_tolerance(self):
        now=self.start+timedelta(seconds=168*3600*.15)
        result=evaluate(self.snapshot,now)
        self.assertFalse(result['allowed'])
        self.assertGreater(datetime.fromisoformat(result['next_eligible_at']),now)

    def test_expired_sample_is_not_a_new_allowance(self):
        self.assertFalse(evaluate(self.snapshot,self.reset+timedelta(seconds=1))['allowed'])

    def test_deadline_and_provider_lock_stop_work(self):
        now=self.start+timedelta(days=2)
        self.assertFalse(evaluate(self.snapshot,now,now)['allowed'])
        self.snapshot['provider_allowed']=False
        self.assertFalse(evaluate(self.snapshot,now)['allowed'])

    def test_exhausted_provider_exposes_its_reset_for_timer(self):
        self.snapshot['provider_allowed']=False
        self.snapshot['windows'][0]['used']=1.
        result=evaluate(self.snapshot,self.start+timedelta(days=2))
        self.assertEqual(datetime.fromisoformat(result['next_eligible_at']),self.reset+timedelta(seconds=60))


if __name__=='__main__':
    unittest.main()
