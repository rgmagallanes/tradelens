import json,tempfile,time,unittest
from pathlib import Path
from backend import mt5_journal as m
class LiveJournalTest(unittest.TestCase):
 def fixture(self,demo):
  now=int(time.time());return dict(version=1,demo=demo,hedging=True,currency='USD',server_utc_offset_seconds=0,timestamp=now,history_from=now-3600,account_key='test-server#123',deals=[],positions=[])
 def test_live_mode_is_preserved_and_account_mode_cannot_mix(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);db=root/'test.sqlite3';export=root/'export.json';d=self.fixture(False);export.write_text(json.dumps(d));result=m.sync(db,export)
   self.assertEqual(result['state'],'connected');self.assertIs(result['demo'],False);self.assertIn('LIVE',result['message'])
   d['demo']=True;export.write_text(json.dumps(d));result=m.sync(db,export);self.assertNotEqual(result['state'],'connected')
   with m.connection(db) as c:self.assertIs(json.loads(c.execute('select payload from mt5_journal_meta').fetchone()[0])['demo'],False)
 def test_mode_must_be_explicit_and_constraints_remain(self):
  for value in [None,'false',0]:
   d=self.fixture(value)
   with self.assertRaises(ValueError):m.validate(d,time.time())
  for field,value in [('hedging',False),('currency','EUR'),('server_utc_offset_seconds',3600)]:
   d=self.fixture(False);d[field]=value
   with self.assertRaises(ValueError):m.validate(d,time.time())
if __name__=='__main__':unittest.main()
