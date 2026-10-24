import tempfile,unittest
from pathlib import Path
from backend import mt5_journal as m
class ProtectionTest(unittest.TestCase):
 def test_current_zero_is_confirmed_unset_and_closed_records_retain_observations(self):
  with tempfile.TemporaryDirectory() as d:
   with m.connection(Path(d)/'test.db') as c:
    opened={'position_id':'1','status':'open'}
    m.protection_records(c,[opened],{'timestamp':1000,'positions':[{'position_id':'1','stop':0,'target':120}],'deals':[]})
    self.assertEqual(opened['protection']['stop']['value'],0);self.assertEqual(opened['protection']['target']['value'],120)
    closed={'position_id':'1','deal_ticket':'2','status':'closed','closed_at':1010}
    m.protection_records(c,[closed],{'timestamp':1020,'positions':[],'deals':[{'ticket':'2','stop':90,'target':120}]})
    self.assertEqual(closed['protection']['stop']['basis'],'exit-deal');self.assertEqual(closed['protection']['stop']['observed_at'],1010)
    self.assertEqual(closed['last_open_protection']['stop']['value'],0)
 def test_missing_fields_stay_unknown_and_later_partial_position_observations_do_not_leak_back(self):
  with tempfile.TemporaryDirectory() as d:
   with m.connection(Path(d)/'test.db') as c:
    opened={'position_id':'1','status':'open'}
    m.protection_records(c,[opened],{'timestamp':1000,'positions':[{'position_id':'1'}],'deals':[]})
    self.assertEqual(opened['protection']['stop'],{'value':None,'basis':'unknown'})
    m.protection_records(c,[],{'timestamp':1100,'positions':[{'position_id':'1','stop':95,'target':130}],'deals':[]})
    closed={'position_id':'1','deal_ticket':'2','status':'closed','closed_at':1050}
    m.protection_records(c,[closed],{'timestamp':1110,'positions':[],'deals':[{'ticket':'2'}]})
    self.assertEqual(closed['protection']['stop']['basis'],'unknown');self.assertNotIn('last_open_protection',closed)
 def test_closed_fill_can_use_observation_when_exit_fields_unavailable(self):
  with tempfile.TemporaryDirectory() as d:
   with m.connection(Path(d)/'test.db') as c:
    m.protection_records(c,[],{'timestamp':1000,'positions':[{'position_id':'1','stop':90}],'deals':[]})
    closed={'position_id':'1','deal_ticket':'2','status':'closed','closed_at':1050}
    m.protection_records(c,[closed],{'timestamp':1110,'positions':[],'deals':[{'ticket':'2'}]})
    self.assertEqual(closed['protection']['stop']['basis'],'open-snapshot');self.assertEqual(closed['protection']['target']['basis'],'unknown')
 def test_second_precision_observation_before_millisecond_entry_is_not_claimed(self):
  with tempfile.TemporaryDirectory() as d:
   with m.connection(Path(d)/'test.db') as c:
    opened={'position_id':'1','status':'open','opened_at':1000.131}
    snapshot={'timestamp':1000,'positions':[{'position_id':'1','stop':90,'target':120}],'deals':[]}
    m.protection_records(c,[opened],snapshot)
    self.assertEqual(opened['protection']['stop']['basis'],'unknown')
    # Unchanged values must still create a valid observation on the next whole second.
    m.protection_records(c,[opened],{**snapshot,'timestamp':1003})
    self.assertEqual(opened['protection']['stop']['observed_at'],1003)
    closed={'position_id':'1','status':'closed','deal_ticket':'2','opened_at':1000.131,'closed_at':1026.647}
    m.protection_records(c,[closed],{'timestamp':1030,'positions':[],'deals':[{'ticket':'2','stop':0,'target':0}]})
    self.assertEqual(closed['protection']['stop']['observed_at'],1026.647)
    self.assertEqual(closed['last_open_protection']['stop']['observed_at'],1003)
 def test_pre_entry_history_is_excluded_from_prior_closed_records(self):
  with tempfile.TemporaryDirectory() as d:
   with m.connection(Path(d)/'test.db') as c:
    m.protection_records(c,[],{'timestamp':1000,'positions':[{'position_id':'1','stop':0,'target':0}],'deals':[]})
    closed={'position_id':'1','status':'closed','deal_ticket':'2','opened_at':1000.131,'closed_at':1026.647}
    m.protection_records(c,[closed],{'timestamp':1030,'positions':[],'deals':[{'ticket':'2','stop':0,'target':0}]})
    self.assertNotIn('last_open_protection',closed)
    self.assertEqual(closed['protection']['target']['basis'],'exit-deal')
if __name__=='__main__':unittest.main()
