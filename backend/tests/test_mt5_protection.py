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
if __name__=='__main__':unittest.main()
