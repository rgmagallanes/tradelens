import ast,json,sqlite3,tempfile,unittest
from pathlib import Path
source=Path(__file__).resolve().parents[1]/'scripts/upload-mt5.py';function=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='read_review_history');namespace={'sqlite3':sqlite3,'math':__import__('math'),'time':__import__('time')};exec(compile(ast.Module(body=[function],type_ignores=[]),str(source),'exec'),namespace)
class HistoryTest(unittest.TestCase):
 def test_backfill_reads_only_completed_supported_recent_candles(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'test.db';now=1800000000
   with sqlite3.connect(path) as c:
    c.execute('create table broker_candles(symbol text,timeframe text,broker_time integer,open real,high real,low real,close real,closed integer)')
    rows=[('XAUUSDm','M5',now-600,100,110,90,101,1),('XAUUSDm','M5',now-300,100,110,90,101,0),('XAUUSDm','M5',now-32*86400,100,110,90,101,1),('XAUUSDm','M5',now,100,110,90,101,1),('XAUUSDm','H4',now-14400,100,110,90,101,1)]
    c.executemany('insert into broker_candles values(?,?,?,?,?,?,?,?)',rows)
   batches=namespace['read_review_history'](path,now);self.assertEqual(len(batches),1);self.assertEqual(batches[0]['timestamp'],1);self.assertEqual(len(batches[0]['bars']),1);self.assertEqual(batches[0]['bars'][0]['time'],now-600)
   with sqlite3.connect(path) as c:self.assertEqual(c.execute('select count(*) from broker_candles').fetchone()[0],5)
 def test_missing_archive_does_not_block_trade_upload(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'test.db'
   with sqlite3.connect(path):pass
   self.assertEqual(namespace['read_review_history'](path),[])
if __name__=='__main__':unittest.main()
