import json,tempfile,unittest
from pathlib import Path
from datetime import datetime,timezone
from backend import mt5_journal as m
NOW=datetime(2026,10,24,10,tzinfo=timezone.utc).timestamp()
def export(offset=10800):
 def deal(ticket,kind,at,side):return dict(ticket=ticket,position_id='10',time=at,symbol='XAUUSD',side=side,entry=kind,price=4000,volume=.01,profit=1,commission=0,swap=0,fee=0,stop=3900,target=4100)
 return dict(version=1,demo=False,hedging=True,currency='USD',server_utc_offset_seconds=offset,timestamp=NOW,history_from=NOW-7*86400,account_key='ErranteSC-Live#123',deals=[deal('1','in',NOW-3600,'buy'),deal('2','out',NOW-1800,'sell')],positions=[])
class ErranteTest(unittest.TestCase):
 def test_explicit_optin_allowlist_and_recent_provenance(self):
  d=export()
  with self.assertRaises(ValueError):m.validate(d,NOW)
  self.assertTrue(m.validate(d,NOW,True))
  for change in [dict(account_key='other-broker#123'),dict(demo=True),dict(server_utc_offset_seconds=14400)]:
   with self.assertRaises(ValueError):m.validate({**d,**change},NOW,True)
  with tempfile.TemporaryDirectory() as folder:
   db=Path(folder)/'test.db';f=Path(folder)/'export.json';f.write_text(json.dumps(d));result=m.sync(db,f,NOW,allow_errante_recent=True)
   self.assertEqual(result['state'],'connected');self.assertIs(result['demo'],False);self.assertEqual(result['timezone_review']['deferred_positions'],0)
   with m.connection(db) as c:
    t=json.loads(c.execute('select payload from mt5_journal_trades').fetchone()[0]);raw=json.loads(c.execute('select payload from mt5_journal_deals where ticket=?',('1',)).fetchone()[0])
   p=t['timestamp_provenance'];self.assertEqual(p['broker_opened_at'],t['opened_at']+10800);self.assertEqual(p['broker_closed_at'],t['closed_at']+10800);self.assertTrue(p['near_clock_change']);self.assertEqual(raw['broker_time'],d['deals'][0]['time']+10800)
   original=t;d['server_utc_offset_seconds']=7200;f.write_text(json.dumps(d));paused=m.sync(db,f,NOW,allow_errante_recent=True)
   self.assertEqual(paused['state'],'unavailable');self.assertIn('offset changed',paused['message'])
   with m.connection(db) as c:self.assertEqual(json.loads(c.execute('select payload from mt5_journal_trades').fetchone()[0]),original)
 def test_older_entries_are_deferred_even_when_exit_is_recent(self):
  d=export();d['deals'][0]['time']=NOW-8*86400
  with tempfile.TemporaryDirectory() as folder:
   db=Path(folder)/'test.db';f=Path(folder)/'export.json';f.write_text(json.dumps(d));result=m.sync(db,f,NOW,allow_errante_recent=True)
   self.assertEqual(result['state'],'connected');self.assertEqual(result['timezone_review']['deferred_positions'],1);self.assertEqual(result['closed_count'],0)
   with m.connection(db) as c:self.assertEqual(c.execute('select count(*) from mt5_journal_deals').fetchone()[0],2);self.assertEqual(c.execute('select count(*) from mt5_journal_trades').fetchone()[0],0)
 def test_review_windows_cover_both_calendars_without_assigning_a_dst_rule(self):
  for date in ['2026-03-08','2026-03-29','2026-10-25','2026-11-01']:
   self.assertTrue(m.near_clock_change(datetime.fromisoformat(date).replace(tzinfo=timezone.utc).timestamp()))
  self.assertFalse(m.near_clock_change(datetime(2026,7,10,tzinfo=timezone.utc).timestamp()))
if __name__=='__main__':unittest.main()
