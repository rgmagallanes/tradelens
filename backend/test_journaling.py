import json,sqlite3
from datetime import datetime,timezone
import pytest
from fastapi.testclient import TestClient
from backend import main,journaling

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(main,'DB',tmp_path/'journal.sqlite3')
    return TestClient(main.app)

def trade(**kw):
    return dict(symbol='BTCUSDm',side='buy',lots=.01,entry=70000,exit=70100,opened_at='2026-09-30T15:55:00Z',closed_at='2026-09-30T16:05:00Z',pnl=4.12,strategy='Test fixture',note='Followed plan',**kw)

def test_manila_closing_day_carry_balances_notes_and_edit(client):
    assert client.post('/api/trading-journal/balance',json={'initial_balance':1000}).status_code==200
    ident=client.post('/api/trading-journal/trades',json=trade()).json()['id']
    sep=client.get('/api/trading-journal?month=2026-09').json()
    oct=client.get('/api/trading-journal?month=2026-10').json()
    assert sep['summary']['pnl']==0 and oct['days'][0]['pnl']==4.12
    assert oct['days'][0]['start_balance']==1000 and oct['days'][1]['start_balance']==1004.12
    assert oct['summary']['closed_count']==1 and oct['summary']['win_rate']==1
    note=dict(source='manual',day='2026-10-01',note='Keep position size consistent')
    assert client.post('/api/trading-journal/notes',json=note).status_code==200
    assert TestClient(main.app).get('/api/trading-journal?month=2026-10').json()['days'][0]['note']==note['note']
    updated=trade();updated['pnl']=-2.5
    assert client.put('/api/trading-journal/trades/'+ident,json=updated).status_code==200
    assert client.get('/api/trading-journal?month=2026-11').json()['summary']['start_balance']==997.5
    assert client.delete('/api/trading-journal/trades/'+ident).status_code==200
    assert client.get('/api/trading-journal?month=2026-10').json()['summary']['closed_count']==0

def test_validation_does_not_create_bad_records(client):
    for patch in [dict(pnl='NaN'),dict(closed_at='2026-09-29T12:00:00Z'),dict(opened_at='2026-09-30T15:55:00'),dict(lots=0),dict(symbol='<script>'),dict(closed_at='2099-01-01T00:00:00Z')]:
        assert client.post('/api/trading-journal/trades',json={**trade(),**patch}).status_code==422
    assert client.get('/api/trading-journal?month=2026-99').status_code==422
    assert client.post('/api/trading-journal/notes',json=dict(source='manual',day='bad',note='bad')).status_code==422
    assert client.get('/api/trading-journal?source=broker').status_code==422
    assert client.get('/api/trading-journal?month=2026-10').json()['summary']['closed_count']==0

def test_sources_separate_and_unknown_close_excluded(client):
    client.post('/api/trading-journal/trades',json=trade())
    stamp=datetime(2026,10,1,tzinfo=timezone.utc).timestamp()
    p=dict(side='sell',lots=.1,entry=70000,status='Closed',pnl=42)
    with main.db() as c:
        c.execute('INSERT INTO records(created,kind,payload) VALUES(?,?,?)',(stamp,'trade',json.dumps(p)))
    sample=client.get('/api/trading-journal?source=sample&month=2026-10').json()
    assert sample['summary']['pnl']==0 and sample['summary']['end_balance']==1000
    assert len(sample['undated_trades'])==1
    assert client.get('/api/trading-journal?source=engine&month=2026-10').json()['summary']['closed_count']==0
    assert client.delete('/api/trading-journal/trades/sample-1').status_code==404

def test_engine_projection_is_read_only_and_close_time_counts(client):
    state=dict(enabled=True,closed=[dict(id='abc',side='buy',lots=.02,entry=100,exit=110,opened_at=1790790000,closed_at=1790876400,pnl=5.25)],position=dict(id='def',side='sell',lots=.01,entry=110,opened_at=1790876400))
    with sqlite3.connect(main.DB) as c:
        c.execute('CREATE TABLE paper_engine(id INTEGER PRIMARY KEY,payload TEXT)')
        c.execute('INSERT INTO paper_engine VALUES(1,?)',(json.dumps(state),))
    out=client.get('/api/trading-journal?source=engine&month=2026-10').json()
    assert out['summary']['closed_count']==1 and out['summary']['pnl']==5.25
    assert len(out['open_positions'])==1
    with sqlite3.connect(main.DB) as c:assert json.loads(c.execute('SELECT payload FROM paper_engine').fetchone()[0])==state
