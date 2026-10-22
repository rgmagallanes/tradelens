import json,time,sqlite3
from fastapi.testclient import TestClient
from backend import main
from backend.history import read_history,archive,INTERVALS

def test_gold_source_isolation(tmp_path,monkeypatch):
 monkeypatch.setattr(main,'DB',tmp_path/'test.sqlite3')
 monkeypatch.setattr(main,'BRIDGE_PATH',tmp_path/'btc-studio-quotes.json')
 client=TestClient(main.app)
 assert client.get('/api/market?source=sample&symbol=XAUUSDm').json()['candles']==[]
 assert client.get('/api/market?source=exness&symbol=XAUUSDm').json()['state']=='missing'
 assert client.get('/api/market?source=exness&symbol=OTHER').status_code==422
 now=time.time(); series={tf:[dict(time=interval,open=3000,high=3010,low=2990,close=3005,closed=True),dict(time=interval*2,open=3005,high=3015,low=3000,close=3010,closed=False)] for tf,interval in INTERVALS.items()}
 data=dict(version=1,timestamp=now,symbol='XAUUSDm',clock='broker-server',demo=True,terminal_connected=True,candles=series)
 path=tmp_path/'xau-studio-candles.json';path.write_text(json.dumps(data))
 quote=dict(version=1,timestamp=now,symbol='XAUUSDm',bid=3010,ask=3010.5,contract_size=100,volume_min=.01,volume_step=.01,quote_age_seconds=1,terminal_connected=True,demo=True,tick_time_msc=600000)
 (tmp_path/'xau-studio-quotes.json').write_text(json.dumps(quote))
 assert read_history(path)['state']=='invalid'
 assert read_history(path,expected_symbol='XAUUSDm')['state']=='valid'
 response=client.get('/api/market?source=exness&symbol=XAUUSDm').json()
 assert response['symbol']=='XAUUSDm' and response['connected'] and response['candles'][0]['open']==3000
 assert client.get('/api/market?source=exness').json()['candles']==[]
 assert client.get('/api/bridge?symbol=XAUUSDm').json()['snapshot']['contract_size']==100
 assert not client.get('/api/bridge').json()['connected']
 # Misplaced BTC data must never be shown under a Gold selection.
 data['symbol']='BTCUSDm';path.write_text(json.dumps(data))
 assert client.get('/api/market?source=exness&symbol=XAUUSDm').json()['state']=='invalid'

def test_archive_keeps_instruments_separate(tmp_path):
 path=tmp_path/'db.sqlite3'
 for symbol,price in [('BTCUSDm',70000),('XAUUSDm',3000)]:
  archive(dict(symbol=symbol,timestamp=1,candles={'M5':[dict(time=300,open=price,high=price,low=price,close=price,closed=True)]}),path)
 with sqlite3.connect(path) as c:
  assert c.execute('SELECT COUNT(*) FROM broker_candles').fetchone()[0]==2
  assert c.execute("SELECT close FROM broker_candles WHERE symbol='XAUUSDm'").fetchone()[0]==3000
