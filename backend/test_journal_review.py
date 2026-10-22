import json,sqlite3
from datetime import datetime,timedelta
import pytest
from fastapi.testclient import TestClient
from backend import main,journal_review,journaling

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(main,'DB',tmp_path/'review.sqlite3');monkeypatch.setattr(journal_review,'HISTORY_PATH',None)
    return TestClient(main.app)

def seed(day='2026-09-19'):
    start=int(datetime.fromisoformat(day+'T00:00:00+08:00').timestamp())
    with sqlite3.connect(main.DB) as c:
        c.execute('CREATE TABLE broker_candles(symbol TEXT,timeframe TEXT,broker_time INTEGER,open REAL,high REAL,low REAL,close REAL,closed INTEGER)')
        c.executemany('INSERT INTO broker_candles VALUES(?,?,?,?,?,?,?,?)',[('BTCUSDm','M5',start+i*300,100,110,90,105,1) for i in range(288)])
    return start

def test_chart_manila_day_and_immutable_snapshot(client):
    start=seed();payload=dict(source='manual',day='2026-09-19',symbol='BTCUSDm',timeframe='M5')
    preview=client.get('/api/trading-journal/chart-review',params=payload).json()
    assert preview['state']=='available' and not preview['saved']
    assert preview['bars'][0]['time']==start and len(preview['bars'])==288
    assert preview['coverage']['missing_completed_bars']==0
    saved=client.post('/api/trading-journal/chart-review',json=payload).json()
    assert saved['saved'] and len(saved['snapshot_sha256'])==64
    with sqlite3.connect(main.DB) as c:c.execute('UPDATE broker_candles SET close=101')
    again=client.get('/api/trading-journal/chart-review',params=payload).json()
    assert again==saved and again['bars'][0]['close']==105
    assert client.post('/api/trading-journal/chart-review',json=payload).json()==saved
    # Snapshot key includes source: the engine sees updated context, not manual's capture.
    engine=client.get('/api/trading-journal/chart-review',params={**payload,'source':'engine'}).json()
    assert not engine['saved'] and engine['bars'][0]['close']==101

def test_no_substitution_for_unrecorded_symbol_or_synthetic_source(client):
    seed();params=dict(source='sample',day='2026-09-19',symbol='BTCUSDm',timeframe='M5')
    assert client.get('/api/trading-journal/chart-review',params=params).json()['state']=='unavailable'
    params.update(source='manual',symbol='XAUUSD')
    assert client.get('/api/trading-journal/chart-review',params=params).json()['bars']==[]
    assert client.post('/api/trading-journal/chart-review',json=params).status_code==422
    assert client.get('/api/trading-journal/chart-review',params={**params,'day':'invalid'}).status_code==422

def test_gap_and_forming_candles_not_filled_in(client):
    start=seed()
    with sqlite3.connect(main.DB) as c:
        c.execute('DELETE FROM broker_candles WHERE broker_time=?',(start+600,))
        c.execute('UPDATE broker_candles SET closed=0 WHERE broker_time=?',(start+900,))
    result=journal_review.load(main.DB,'manual','2026-09-19','BTCUSDm','M5',now=start+86400)
    assert result['coverage']['bars']==286 and result['coverage']['missing_completed_bars']==2
    assert all(b['time'] not in (start+600,start+900) for b in result['bars'])

def test_snapshot_trade_markers_are_frozen_and_source_scoped(client):
    start=seed()
    ident=journaling.add_trade(main.DB,dict(symbol='BTCUSDM',side='buy',lots=.01,entry=100,exit=110,opened_at=start+3600,closed_at=start+3900,pnl=.1,status='closed',strategy='',note='Original'))
    payload=dict(source='manual',day='2026-09-19',symbol='BTCUSDM',timeframe='M5')
    saved=client.post('/api/trading-journal/chart-review',json=payload).json()
    assert [t['id'] for t in saved['trades']]==[ident]
    with journaling.connect(main.DB) as c:c.execute('DELETE FROM journal_trades WHERE id=?',(ident,))
    assert client.get('/api/trading-journal/chart-review',params=payload).json()['trades']==saved['trades']
    assert client.get('/api/trading-journal/chart-review',params={**payload,'source':'engine'}).json()['trades']==[]

def test_specific_trade_reviews_have_independent_markers_and_snapshot_keys(client):
    start=seed()
    ids=[]
    for n in range(2):
        ids.append(journaling.add_trade(main.DB,dict(symbol='BTCUSDM',side='buy' if n==0 else 'sell',lots=.01,entry=100+n,exit=105,opened_at=start+3600+n*600,closed_at=start+3900+n*600,pnl=.1,status='closed',strategy='',note='')))
    params=dict(source='manual',day='2026-09-19',symbol='BTCUSDm',timeframe='M5',trade_id=ids[0])
    first=client.post('/api/trading-journal/chart-review',json=params).json()
    assert first['saved'] and [t['id'] for t in first['trades']]==[ids[0]]
    with sqlite3.connect(main.DB) as c:c.execute('UPDATE broker_candles SET close=101')
    second=client.get('/api/trading-journal/chart-review',params={**params,'trade_id':ids[1]}).json()
    assert not second['saved'] and second['bars'][0]['close']==101 and [t['id'] for t in second['trades']]==[ids[1]]
    assert client.get('/api/trading-journal/chart-review',params=params).json()==first
    assert client.get('/api/trading-journal/chart-review',params={**params,'source':'engine'}).status_code==422
    assert client.get('/api/trading-journal/chart-review',params={**params,'trade_id':'unknown'}).status_code==422
