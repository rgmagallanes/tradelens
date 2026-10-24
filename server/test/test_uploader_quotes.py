import ast,json,math,tempfile,unittest
from pathlib import Path
# Load only the pure collection function, without CLI parsing, tokens or networking.
source=Path(__file__).resolve().parents[1]/'scripts/upload-mt5.py'
function=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='read_markets')
namespace={'json':json,'math':math}
exec(compile(ast.Module(body=[function],type_ignores=[]),str(source),'exec'),namespace)
class QuoteCollectionTest(unittest.TestCase):
 def test_unknown_tick_age_does_not_block_candles_or_masquerade_as_fresh(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder)
   for age in [-1,0,120,None]:
    market=dict(symbol='XAUUSDm',timestamp=100,demo=True,terminal_connected=True,clock='broker-server',server_utc_offset_seconds=0,candles={'M5':[]})
    quote=dict(version=1,symbol='XAUUSDm',timestamp=100,bid=100,ask=101,demo=True,terminal_connected=True,quote_age_seconds=age)
    (root/'xau-studio-candles.json').write_text(json.dumps(market));(root/'xau-studio-quotes.json').write_text(json.dumps(quote))
    result=namespace['read_markets'](root)
    self.assertEqual(len(result),1);self.assertEqual(result[0]['candles'],{'M5':[]})
    self.assertEqual('quote'in result[0],age is not None and age>=0)
    if 'quote'in result[0]:self.assertEqual(result[0]['quote']['quote_age_seconds'],age)
if __name__=='__main__':unittest.main()
