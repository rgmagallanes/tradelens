import json,sqlite3
import pytest
from fastapi.testclient import TestClient
from backend import journaling,trade_ideas as ideas,trade_postmortem as pm,main,journal_review
NOW=1800057600
PLAN=dict(title='Defined retest',symbol='BTCUSDm',side='buy',setup='Retest',reason='Confirmed level hold; invalidate below stop',entry=100,stop=95,target=110,risk_budget=10)
@pytest.fixture
def setup(tmp_path,monkeypatch):
 p=tmp_path/'ideas.sqlite3';monkeypatch.setattr(main,'DB',p);monkeypatch.setattr(journal_review,'HISTORY_PATH',None)
 return p,TestClient(main.app)
def seed_mt5(p,rows):
 with journaling.connect(p) as c:
  c.execute('CREATE TABLE IF NOT EXISTS mt5_journal_trades(id TEXT PRIMARY KEY,payload TEXT NOT NULL)')
  for row in rows:c.execute('INSERT OR REPLACE INTO mt5_journal_trades VALUES(?,?)',(row['id'],json.dumps(row)))
def trade(ident,position='101',status='open',**kw):
 return dict(id=ident,source='mt5',position_id=position,symbol='BTCUSDm',side='buy',lots=.5,entry=100,opened_at=NOW+60,status=status,closed_at=NOW+600 if status=='closed' else None,exit=105 if status=='closed' else None,pnl=5 if status=='closed' else None,floating_pnl=3 if status=='open' else None,strategy='',note='',**kw)

def test_original_timestamp_and_snapshot_are_immutable_and_causal(setup):
 p,_=setup
 with sqlite3.connect(p) as c:
  c.execute('CREATE TABLE broker_candles(symbol TEXT,timeframe TEXT,broker_time INTEGER,open REAL,high REAL,low REAL,close REAL,closed INTEGER)')
  c.executemany('INSERT INTO broker_candles VALUES(?,?,?,?,?,?,?,?)',[('BTCUSDm','M5',NOW-300,100,110,90,105,1),('BTCUSDm','M5',NOW,100,999,90,105,1)])
 ident=ideas.create(p,'mt5',PLAN,now=NOW);r=ideas.listing(p,'mt5',now=NOW)['ideas'][0]
 assert r['created_at']==NOW and len(r['snapshot']['bars'])==1 and r['snapshot']['bars'][0]['high']==110
 with sqlite3.connect(p) as c:c.execute('UPDATE broker_candles SET high=1000')
 assert ideas.listing(p,'mt5',now=NOW+999)['ideas'][0]['snapshot']==r['snapshot']
 assert r['timing']=='Saved plan · awaiting execution'

def test_partial_exits_and_remaining_position_keep_link_and_do_not_double_count(setup):
 p,_=setup;i=ideas.create(p,'mt5',PLAN,now=NOW);seed_mt5(p,[trade('mt5-open-101')]);ideas.assign(p,'mt5','mt5-open-101',i)
 with journaling.connect(p) as c:c.execute("DELETE FROM mt5_journal_trades WHERE id='mt5-open-101'")
 closed=trade('mt5-close-1',status='closed');closed['lots']=.2
 opened=trade('mt5-open-101');opened['lots']=.3
 seed_mt5(p,[closed,opened]);r=ideas.listing(p,'mt5',now=NOW+100)['ideas'][0]
 assert r['positions']==1 and r['closed_rows']==1 and r['open_rows']==1 and r['closed_net']==5 and r['floating_pnl']==3
 assert r['timing']=='Saved before all linked entries' and len(ideas.listing(p,'mt5')['ungrouped'])==0
 assert r['closed_lots']==.2 and r['open_lots']==.3
 with journaling.connect(p) as c:c.execute("DELETE FROM mt5_journal_trades WHERE id='mt5-open-101'")
 last=trade('mt5-close-2',status='closed');last.update(lots=.3,pnl=-2)
 seed_mt5(p,[last]);r=ideas.listing(p,'mt5')['ideas'][0]
 assert r['status']=='closed' and r['closed_net']==3 and r['positions']==1
 assert journaling.snapshot(p,'mt5',journaling.day(NOW)[:7])['summary']['pnl']==3

def test_multiple_positions_grouped_and_retrospective_plan_labeled(setup):
 p,_=setup;seed_mt5(p,[trade('a',position='1',status='closed'),trade('b',position='2')])
 i=ideas.create(p,'mt5',PLAN,now=NOW+120)
 for ident in ['a','b']:ideas.assign(p,'mt5',ident,i)
 r=ideas.listing(p,'mt5')['ideas'][0]
 assert r['positions']==2 and r['closed_net']==5 and r['floating_pnl']==3 and r['timing'].startswith('Retrospective')
 assert r['plan']==PLAN

def test_source_symbol_direction_guards_and_assignment_audit(setup):
 p,_=setup;i=ideas.create(p,'manual',PLAN,now=NOW);seed_mt5(p,[trade('a')])
 with pytest.raises(ValueError,match='this source'):ideas.assign(p,'mt5','a',i)
 short=ideas.create(p,'mt5',{**PLAN,'side':'sell','stop':105,'target':90},now=NOW)
 with pytest.raises(ValueError,match='same symbol'):ideas.assign(p,'mt5','a',short)
 gold=ideas.create(p,'mt5',{**PLAN,'symbol':'XAUUSDm'},now=NOW)
 with pytest.raises(ValueError,match='same symbol'):ideas.assign(p,'mt5','a',gold)
 good=ideas.create(p,'mt5',PLAN,now=NOW);ideas.assign(p,'mt5','a',good);ideas.assign(p,'mt5','a',good)
 ideas.assign(p,'mt5','a',None)
 assert len(ideas.listing(p,'mt5')['ungrouped'])==1
 with ideas.connection(p) as c:assert c.execute('SELECT COUNT(*) FROM journal_idea_link_audit').fetchone()[0]==2

def test_no_broker_context_substitution_for_sample_or_missing_history(setup):
 p,_=setup
 for source in ['sample','manual']:
  ideas.create(p,source,PLAN,now=NOW)
  assert ideas.listing(p,source)['ideas'][0]['snapshot']['bars']==[]

def test_api_validates_levels_and_does_not_allow_original_plan_edits(setup):
 p,c=setup
 assert c.post('/api/trading-journal/ideas',json=dict(source='mt5',plan={**PLAN,'stop':110})).status_code==422
 result=c.post('/api/trading-journal/ideas',json=dict(source='mt5',plan=PLAN));assert result.status_code==200
 ident=result.json()['id']
 assert c.put('/api/trading-journal/ideas/'+ident,json={'plan':{**PLAN,'stop':90}}).status_code in (404,405)
 assert c.get('/api/trading-journal/ideas',params={'source':'mt5'}).json()['ideas'][0]['plan']==PLAN
 assert c.get('/api/trading-journal/ideas',params={'source':'manual'}).json()['ideas']==[]

def test_linked_original_is_available_to_postmortem_without_overwriting_it(setup):
 p,_=setup;i=ideas.create(p,'mt5',PLAN,now=NOW);seed_mt5(p,[trade('a',status='closed')]);ideas.assign(p,'mt5','a',i)
 review=pm.review(p,'mt5','a');assert review['evidence']['linked_trade_plan']['immutable']
 assert review['evidence']['plan_origin']=='linked_saved_plan' and review['evidence']['plan']['original_stop']==95
 assert review['evidence']['facts']['price_r']==1
 pm.save_plan(p,'mt5','a',pm.Plan(original_stop=90,original_target=120).model_dump())
 assert ideas.listing(p,'mt5')['ideas'][0]['plan']['stop']==95
 assert pm.review(p,'mt5','a')['evidence']['plan_origin']=='retrospective_review_notes'
 assert pm.review(p,'mt5','a')['evidence']['risk_level_basis']=='Retrospective review-note levels'

def test_stale_snapshot_is_not_claimed_live(setup):
 p,_=setup;seed_mt5(p,[trade('a')])
 with ideas.connection(p) as c:
  c.execute('CREATE TABLE mt5_journal_meta(id INTEGER PRIMARY KEY,payload TEXT)')
  c.execute('INSERT INTO mt5_journal_meta VALUES(1,?)',(json.dumps({'timestamp':NOW}),))
 assert ideas.listing(p,'mt5',now=NOW+2)['floating_fresh']
 assert not ideas.listing(p,'mt5',now=NOW+31)['floating_fresh']
