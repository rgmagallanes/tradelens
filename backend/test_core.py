import pytest
from fastapi.testclient import TestClient
from backend import main
@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(main,'DB',tmp_path/'test.sqlite3')
    return TestClient(main.app)
def test_costs_and_rounding(client):
    p={'entry':70000,'stop':69900,'target':70200,'risk':5,'spread':20,'slippage':5}
    r=client.post('/api/plan',json=p).json()
    assert r['lots']==.03 and r['estimated_loss']==3.9 and r['estimated_gain']==5.1
    assert client.post('/api/simulate',json=p).status_code==422
    t=client.post('/api/simulate',json={**p,'confirmed':True}).json()
    assert client.post('/api/simulate',json={**p,'confirmed':True}).status_code==409
    closed=client.post(f"/api/trades/{t['id']}/close",json={'price':70200}).json()
    assert closed['pnl']==5.1
    assert client.post(f"/api/trades/{t['id']}/close",json={'price':70200}).status_code==409
def test_invalid_and_small(client):
    assert client.post('/api/plan',json={'entry':70000,'stop':70100,'target':70200,'risk':5}).status_code==422
    r=client.post('/api/plan',json={'entry':70000,'stop':60000,'target':72000,'risk':1}).json()
    assert not r['eligible'] and r['lots']==0

def test_bridge_fresh_stale_and_invalid(tmp_path):
    import json
    path=tmp_path/'quotes.json'
    assert main.bridge_status(path,1000)['state']=='missing'
    quote=dict(version=1,timestamp=999,symbol='BTCUSDm',bid=70000,ask=70020,contract_size=1,volume_min=.01,volume_step=.01,quote_age_seconds=2,terminal_connected=True,demo=True)
    path.write_text(json.dumps(quote))
    status=main.bridge_status(path,1000)
    assert status['connected'] and status['spread']==20
    assert not main.bridge_status(path,1020)['connected']
    quote['quote_age_seconds']=30
    path.write_text(json.dumps(quote))
    assert not main.bridge_status(path,1000)['connected']
    quote.update(quote_age_seconds=0,demo=False)
    path.write_text(json.dumps(quote))
    assert main.bridge_status(path,1000)['state']=='non-demo'
    quote.update(demo=True,bid=float('nan'))
    path.write_text(json.dumps(quote))
    assert main.bridge_status(path,1000)['state']=='invalid'
    path.write_text('{')
    assert main.bridge_status(path,1000)['state']=='invalid'

def test_history_validation_and_archive(tmp_path):
    import json,sqlite3
    from backend.history import read_history,archive,INTERVALS
    path=tmp_path/'candles.json'
    assert read_history(path)['state']=='missing'
    data=dict(version=1,timestamp=1000,symbol='BTCUSDm',clock='broker-server',candles={tf:[dict(time=interval,open=100,high=110,low=90,close=105,closed=True),dict(time=interval*2,open=105,high=115,low=100,close=110,closed=False)] for tf,interval in INTERVALS.items()})
    path.write_text(json.dumps(data));assert read_history(path,1001)['state']=='valid'
    archive(data,tmp_path/'archive.sqlite3');archive(data,tmp_path/'archive.sqlite3')
    with sqlite3.connect(tmp_path/'archive.sqlite3') as c: assert c.execute('SELECT COUNT(*) FROM broker_candles').fetchone()[0]==8
    data['candles']['M5'][0]['high']=99
    path.write_text(json.dumps(data));assert read_history(path,1001)['state']=='invalid'

def test_exness_never_falls_back_to_sample(client,tmp_path,monkeypatch):
    monkeypatch.setattr(main,'BRIDGE_PATH',tmp_path/'quotes.json')
    r=client.get('/api/market?source=exness&tf=M5').json()
    assert r['source']=='exness' and r['candles']==[] and not r['connected']
    assert client.get('/api/market?tf=M1').status_code==422

def test_live_candle_endpoint_fixture(client,tmp_path,monkeypatch):
    import json,time
    from backend.history import INTERVALS
    now=int(time.time());quote=tmp_path/'quotes.json';monkeypatch.setattr(main,'BRIDGE_PATH',quote)
    quote.write_text(json.dumps(dict(version=1,timestamp=now,symbol='BTCUSDm',bid=100,ask=101,contract_size=1,volume_min=.01,volume_step=.01,quote_age_seconds=0,terminal_connected=True,demo=True,tick_time_msc=now*1000)))
    data=dict(version=1,timestamp=now,symbol='BTCUSDm',clock='broker-server',demo=True,terminal_connected=True,candles={tf:[dict(time=(now//n-1)*n,open=100,high=110,low=90,close=105,closed=True),dict(time=now//n*n,open=105,high=115,low=100,close=110,closed=False)] for tf,n in INTERVALS.items()})
    history=quote.with_name('btc-studio-candles.json');history.write_text(json.dumps(data))
    r=client.get('/api/market?source=exness&tf=M15').json()
    assert r['connected'] and r['source']=='exness' and r['research_m1_count']==2 and r['candles']==data['candles']['M15']
    data['timestamp']=now-60;history.write_text(json.dumps(data))
    r=client.get('/api/market?source=exness&tf=M15').json()
    assert not r['connected'] and r['state']=='stale' and r['candles']==data['candles']['M15']

def test_confirmed_settings_roundtrip_after_new_client(client,tmp_path,monkeypatch):
    config=dict(commission_per_lot_side=0,commission_confirmed=True,commission_source='Isolated test fixture only',parity_verified=True,verification_note='Isolated fixture parity; not a real verification')
    saved=client.post('/api/engine/config',json=config)
    assert saved.status_code==200 and saved.json()['config']==config
    from fastapi.testclient import TestClient
    refreshed=TestClient(main.app)
    assert refreshed.get('/api/engine').json()['config']==config
    bad={**config,'verification_note':''}
    assert refreshed.post('/api/engine/config',json=bad).status_code==422
    assert refreshed.get('/api/engine').json()['config']==config

def test_optional_h4_and_tick_volume_feed_compatibility(client,tmp_path,monkeypatch):
    import json,time
    from backend.history import INTERVALS,read_history
    now=int(time.time());q=tmp_path/'quotes.json';monkeypatch.setattr(main,'BRIDGE_PATH',q)
    q.write_text(json.dumps(dict(version=1,timestamp=now,symbol='BTCUSDm',bid=100,ask=101,contract_size=1,volume_min=.01,volume_step=.01,quote_age_seconds=0,terminal_connected=True,demo=True,tick_time_msc=now*1000)))
    def series(interval):return [dict(time=(now//interval-1)*interval,open=100,high=110,low=90,close=105,closed=True),dict(time=now//interval*interval,open=105,high=115,low=100,close=110,closed=False)]
    data=dict(version=1,timestamp=now,symbol='BTCUSDm',clock='broker-server',demo=True,terminal_connected=True,candles={tf:series(n) for tf,n in INTERVALS.items()});path=q.with_name('btc-studio-candles.json');path.write_text(json.dumps(data))
    assert client.get('/api/market?source=exness&tf=M5').json()['connected']
    missing=client.get('/api/market?source=exness&tf=H4').json()
    assert not missing['connected'] and missing['candles']==[] and missing['state']=='missing-timeframe'
    data['candles']['H4']=series(14400)
    for bars in data['candles'].values():
        for b in bars:b.update(tick_volume=500,real_volume=0)
    path.write_text(json.dumps(data))
    h4=client.get('/api/market?source=exness&tf=H4').json()
    assert h4['connected'] and h4['candles']==data['candles']['H4'] and h4['candles'][0]['tick_volume']==500
    data['candles']['H4'][0]['time']+=60;path.write_text(json.dumps(data));assert read_history(path)['state']=='invalid'
    data['candles']['H4']=series(14400);data['candles']['M5'][0]['tick_volume']=True;path.write_text(json.dumps(data));assert read_history(path)['state']=='invalid'
    sample=client.get('/api/market?source=sample&tf=H4').json()
    assert sample['source']=='sample' and sample['candles'][1]['time']-sample['candles'][0]['time']==14400
    assert all(b['tick_volume']>=0 for b in sample['candles'])

def test_volume_archive_migrates_old_schema_without_inventing_volume(tmp_path):
    import sqlite3
    from backend.history import archive
    path=tmp_path/'old.sqlite3'
    with sqlite3.connect(path) as c:
        c.execute('CREATE TABLE broker_candles(symbol TEXT,timeframe TEXT,broker_time INTEGER,open REAL,high REAL,low REAL,close REAL,closed INTEGER,received_at REAL,export_timestamp REAL,PRIMARY KEY(symbol,timeframe,broker_time))')
        c.execute("INSERT INTO broker_candles VALUES('BTCUSDm','M5',300,100,110,90,105,1,1000,1000)")
    data=dict(symbol='BTCUSDm',timestamp=1001,candles={'H4':[dict(time=14400,open=100,high=110,low=90,close=105,closed=True,tick_volume=1234,real_volume=0)]})
    archive(data,path);archive(data,path)
    with sqlite3.connect(path) as c:
        assert c.execute('SELECT COUNT(*) FROM broker_candles').fetchone()[0]==2
        assert c.execute("SELECT tick_volume,real_volume FROM broker_candles WHERE timeframe='M5'").fetchone()==(None,None)
        assert c.execute("SELECT tick_volume,real_volume FROM broker_candles WHERE timeframe='H4'").fetchone()==(1234,0)
