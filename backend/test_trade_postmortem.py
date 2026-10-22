import json,sqlite3
from datetime import datetime
import pytest,httpx
from backend import main,journaling,journal_review,trade_postmortem as pm
from fastapi.testclient import TestClient
@pytest.fixture
def setup(tmp_path,monkeypatch):
    path=tmp_path/'review.sqlite3';monkeypatch.setattr(main,'DB',path);monkeypatch.setattr(journal_review,'HISTORY_PATH',None)
    monkeypatch.delenv('OPENAI_API_KEY',raising=False);monkeypatch.delenv('TRADELENS_AI_MODEL',raising=False)
    start=int(datetime.fromisoformat('2026-09-19T10:00:00+08:00').timestamp())
    with sqlite3.connect(path) as c:
        c.execute('CREATE TABLE broker_candles(symbol TEXT,timeframe TEXT,broker_time INTEGER,open REAL,high REAL,low REAL,close REAL,closed INTEGER)')
        c.executemany('INSERT INTO broker_candles VALUES(?,?,?,?,?,?,?,?)',[('BTCUSDm','M5',start+i*300,100,110 if i!=4 else 999,90,105,1) for i in range(5)])
    ident=journaling.add_trade(path,dict(symbol='BTCUSDm',side='buy',lots=.1,entry=100,exit=95,opened_at=start+60,closed_at=start+1190,status='closed',pnl=-.5,strategy='',note='Private unrelated original note',account='must-not-send',stop=97,target=115))
    return path,ident,start,TestClient(main.app)

def test_facts_exclude_boundary_and_post_exit_candles_and_final_levels(setup):
    p,i,start,_=setup;r=pm.review(p,'manual',i);f=r['evidence']['facts']
    assert f['holding_m5_bars']==2 and f['expected_holding_m5_bars']==2
    assert f['mfe_price_estimate']==10 and f['mae_price_estimate']==10
    assert f['directional_price_move']==-5 and f['planned_rr'] is None and f['price_r'] is None
    assert 'must-not-send' not in json.dumps(r) and 'Private unrelated' not in json.dumps(r)
    assert r['ai']['configured'] is False

def test_plan_r_and_review_persistence_staleness_and_source_isolation(setup):
    p,i,_,_=setup;plan=pm.Plan(setup='Test',reason='Defined trigger',original_stop=95,original_target=110)
    r=pm.save_plan(p,'manual',i,plan.model_dump());assert r['evidence']['facts']['planned_rr']==2 and r['evidence']['facts']['price_r']==-1
    first=pm.save_local(p,'manual',i);again=pm.save_local(p,'manual',i)
    assert first['saved_reviews']==again['saved_reviews'] and len(again['saved_reviews'])==1
    changed=pm.save_plan(p,'manual',i,{**plan.model_dump(),'lesson':'One change'})
    assert changed['fingerprint']!=changed['saved_reviews'][0]['fingerprint']
    assert changed['saved_reviews'][0]['evidence']['plan']['lesson']==''
    with pytest.raises(ValueError,match='selected source'):pm.review(p,'mt5',i)

def test_sell_excursions_and_invalid_risk(setup):
    p,i,_,_=setup
    with journaling.connect(p) as c:
        row=json.loads(c.execute('SELECT payload FROM journal_trades WHERE id=?',(i,)).fetchone()[0]);row.update(side='sell',exit=105)
        c.execute('UPDATE journal_trades SET payload=? WHERE id=?',(json.dumps(row),i))
    r=pm.save_plan(p,'manual',i,pm.Plan(original_stop=105,original_target=90).model_dump())
    assert r['evidence']['facts']['price_r']==-1 and r['evidence']['facts']['planned_rr']==2
    r=pm.save_plan(p,'manual',i,pm.Plan(original_stop=90,original_target=110).model_dump())
    assert r['evidence']['facts']['price_r'] is None and r['evidence']['facts']['planned_rr'] is None

def test_missing_history_and_open_trade_rejection(setup):
    p,i,_,_=setup
    with sqlite3.connect(p) as c:c.execute('DELETE FROM broker_candles')
    r=pm.review(p,'manual',i)
    assert r['evidence']['facts']['mfe_price_estimate'] is None
    with journaling.connect(p) as c:
        payload=json.loads(c.execute('SELECT payload FROM journal_trades WHERE id=?',(i,)).fetchone()[0]);payload.update(status='open')
        c.execute('UPDATE journal_trades SET payload=? WHERE id=?',(json.dumps(payload),i))
    with pytest.raises(ValueError,match='closed trades'):pm.review(p,'manual',i)

def test_api_rejects_invalid_plan_and_no_config_or_consent_without_network(setup,monkeypatch):
    p,i,_,client=setup
    original=httpx.Client.post
    def guard(self,url,**kw):
        if str(url).startswith('https://api.openai.com'):pytest.fail('No outbound request permitted')
        return original(self,url,**kw)
    monkeypatch.setattr(httpx.Client,'post',guard)
    r=client.get('/api/trading-journal/postmortem',params={'source':'manual','trade_id':i});assert r.status_code==200
    body=dict(source='manual',trade_id=i,fingerprint=r.json()['fingerprint'])
    assert client.post('/api/trading-journal/postmortem/ai',json=body).status_code==422
    assert client.post('/api/trading-journal/postmortem/ai',json={**body,'consent':True}).status_code==422
    assert client.post('/api/trading-journal/postmortem/plan',json=dict(source='manual',trade_id=i,plan={'original_stop':-1})).status_code==422
    assert client.post('/api/trading-journal/postmortem/local',json=dict(source='manual',trade_id=i)).status_code==200

def test_ai_allowlisted_payload_response_saved_once(setup,monkeypatch):
    p,i,_,_=setup;monkeypatch.setenv('OPENAI_API_KEY','test-only-not-a-real-key');monkeypatch.setenv('TRADELENS_AI_MODEL','test-model')
    coaching=dict(summary='Evidence-based test',strengths=[],improvements=['Document trigger'],next_experiment='Freeze a rule',missing_evidence=['Original plan'])
    calls=[]
    def fake(self,url,**kw):
        assert url=='https://api.openai.com/v1/responses';assert kw['json']['store'] is False
        assert 'must-not-send' not in json.dumps(kw['json']) and 'Private unrelated' not in json.dumps(kw['json'])
        calls.append(kw['json'])
        return httpx.Response(200,json={'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(coaching)}]}]})
    monkeypatch.setattr(httpx.Client,'post',fake)
    r=pm.review(p,'manual',i)
    with pytest.raises(ValueError,match='changed'):pm.generate(p,'manual',i,True,'0'*64)
    result=pm.generate(p,'manual',i,True,r['fingerprint']);assert result['saved_reviews'][0]['kind']=='ai'
    assert result['saved_reviews'][0]['coaching']==coaching
    pm.generate(p,'manual',i,True,r['fingerprint']);assert len(calls)==1

def test_failed_or_malformed_provider_response_preserves_saved_reviews(setup,monkeypatch):
    p,i,_,_=setup;monkeypatch.setenv('OPENAI_API_KEY','test-only');monkeypatch.setenv('TRADELENS_AI_MODEL','test-model')
    r=pm.save_local(p,'manual',i)
    for payload in [{'status':'incomplete'},{'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':'{}'}]}]}]:
        monkeypatch.setattr(httpx.Client,'post',lambda *a,**k:httpx.Response(200,json=payload))
        with pytest.raises(ValueError):pm.generate(p,'manual',i,True,r['fingerprint'])
    assert len(pm.review(p,'manual',i)['saved_reviews'])==1
