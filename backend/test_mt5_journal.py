import json,sqlite3
import pytest
from backend import mt5_journal as m,journaling
NOW=1800057600

def deal(ticket,entry='in',volume=1,side='buy',stamp=NOW-600,**kw):
 return dict(ticket=str(ticket),position_id='100',time=stamp,symbol='XAUUSDm',side=side,entry=entry,price=3000 if entry=='in' else 3010,volume=volume,profit=0,commission=0,swap=0,fee=0,stop=2900,target=3100,**kw)
def envelope(deals=None,positions=None,**kw):
 return dict(version=1,demo=True,hedging=True,currency='USD',server_utc_offset_seconds=0,account_key='demo-server#123',timestamp=NOW,history_from=NOW-7*86400,deals=deals or [],positions=positions or [],**kw)
def sync(tmp_path,d):
 f=tmp_path/'export.json';f.write_text(json.dumps(d));return m.sync(tmp_path/'db.sqlite3',f,NOW+1)
def rows(tmp_path):
 with m.connection(tmp_path/'db.sqlite3') as c:return [json.loads(r[0]) for r in c.execute('SELECT payload FROM mt5_journal_trades ORDER BY id')]

def test_partial_closes_costs_remainders_and_no_duplicate_restart(tmp_path):
 entry=deal(1);entry['commission']=-2
 close=deal(2,'out',.4,'sell',NOW-300);close.update(profit=40,commission=-.4,swap=-1,fee=-.1)
 d=envelope([entry,close],[dict(position_id='100',volume=.6,floating_pnl=15)])
 assert sync(tmp_path,d)['state']=='connected'
 r=rows(tmp_path);closed=next(x for x in r if x['status']=='closed');opened=next(x for x in r if x['status']=='open')
 assert closed['pnl']==37.7 and closed['allocated_entry_costs']==-.8
 assert opened['lots']==pytest.approx(.6) and opened['unallocated_entry_costs']==-1.2
 assert sync(tmp_path,d)['deals']==2 and len(rows(tmp_path))==2
 final=deal(3,'out',.6,'sell',NOW-100);final.update(profit=-10,commission=-.6)
 d=envelope([entry,close,final]);assert sync(tmp_path,d)['open_count']==0
 r=rows(tmp_path);assert len(r)==2 and all(x['status']=='closed' for x in r)
 assert sum(x['pnl'] for x in r)==pytest.approx(25.9)
 month=__import__('datetime').datetime.fromtimestamp(NOW,journaling.TZ).strftime('%Y-%m')
 snap=journaling.snapshot(tmp_path/'db.sqlite3','mt5',month)
 assert snap['initial_balance']==0 and snap['summary']['pnl']==25.9 and snap['summary']['closed_count']==2
 assert journaling.snapshot(tmp_path/'db.sqlite3','manual',month)['summary']['pnl']==0

def test_complete_old_entry_lifecycle_is_used_but_old_exits_outside_window_excluded(tmp_path):
 a=deal(1,stamp=NOW-10*86400);a['commission']=-2
 b=deal(2,'out',.5,'sell',NOW-8*86400);b['profit']=20
 c=deal(3,'out',.5,'sell',NOW-60);c['profit']=10
 assert sync(tmp_path,envelope([a,b,c]))['state']=='connected'
 r=rows(tmp_path);assert len(r)==1 and r[0]['pnl']==9 and r[0]['opened_at']==a['time']

def test_real_account_changes_stale_netting_invalid_and_duplicates_never_alter_saved(tmp_path):
 a=deal(1);b=deal(2,'out',1,'sell',NOW-60);b['profit']=20
 sync(tmp_path,envelope([a,b]));saved=rows(tmp_path)
 for patch in [dict(demo=False),dict(account_key='other-account'),dict(timestamp=NOW-60),dict(hedging=False),dict(currency='EUR'),dict(server_utc_offset_seconds=3600),dict(deals=[a,a]),dict(deals=[{**a,'entry':'inout'}]),dict(deals=[{**a,'price':float('nan')}])]:
  d=envelope([a,b]);d.update(patch);assert sync(tmp_path,d)['state']=='unavailable';assert rows(tmp_path)==saved
 f=tmp_path/'export.json';f.write_text('{');assert m.sync(tmp_path/'db.sqlite3',f,NOW+1)['state']=='unavailable';assert rows(tmp_path)==saved

def test_orphan_and_volume_mismatch_are_quarantined_and_valid_positions_import(tmp_path):
 orphan=deal(2,'out',1,'sell',NOW-50)
 d=envelope([orphan]);s=sync(tmp_path,d);assert s['issues'] and rows(tmp_path)==[]
 # Fresh isolated database: same exit with its actual entry resolves.
 d=envelope([deal(1),orphan]);assert sync(tmp_path,d)['issues']==[];assert len(rows(tmp_path))==1
 bad=envelope([deal(1),orphan],[dict(position_id='100',volume=1,floating_pnl=0)])
 assert sync(tmp_path,bad)['issues'];assert len(rows(tmp_path))==1

def test_missing_export_and_empty_demo_account_are_explicit(tmp_path):
 assert m.sync(tmp_path/'db.sqlite3',tmp_path/'missing',NOW)['state']=='waiting'
 assert sync(tmp_path,envelope())['deals']==0
 assert rows(tmp_path)==[]


def test_api_journal_status_and_notes_are_isolated(tmp_path,monkeypatch):
 from backend import main
 from fastapi.testclient import TestClient
 monkeypatch.setattr(main,'DB',tmp_path/'db.sqlite3');monkeypatch.setattr(main,'BRIDGE_PATH',tmp_path/'btc-studio-quotes.json')
 monkeypatch.setattr(m.time,'time',lambda:NOW+1)
 from datetime import datetime
 class FrozenDateTime(datetime):
  @classmethod
  def now(cls,tz=None):return datetime.fromtimestamp(NOW+1,tz)
 monkeypatch.setattr(main,'datetime',FrozenDateTime)
 a=deal(1);b=deal(2,'out',1,'sell',NOW-60);b['profit']=20
 (tmp_path/'studio-trades.json').write_text(json.dumps(envelope([a,b])))
 client=TestClient(main.app)
 status=client.get('/api/trading-journal/mt5-status').json();assert status['state']=='connected';assert status['closed_today']==20;assert status['journal_day']==journaling.day(NOW);assert 'account' not in status and 'hash' not in status
 month=__import__('datetime').datetime.fromtimestamp(NOW,journaling.TZ).strftime('%Y-%m')
 snap=client.get('/api/trading-journal',params={'source':'mt5','month':month}).json();assert snap['summary']['pnl']==20
 d=next(d['date'] for d in snap['days'] if d['closed_count'])
 assert client.post('/api/trading-journal/notes',json={'source':'mt5','day':d,'note':'Lesson'}).status_code==200
 assert client.get('/api/trading-journal',params={'source':'mt5','month':month}).json()['summary']['closed_count']==1
 assert client.get('/api/trading-journal',params={'source':'manual','month':month}).json()['summary']['closed_count']==0
 assert client.delete('/api/trading-journal/trades/mt5-close-2').status_code==404

def test_floating_values_update_without_changing_realized_ledger(tmp_path):
 entry=deal(1);positions=[dict(position_id='100',volume=1,floating_pnl=15)]
 a=sync(tmp_path,envelope([entry],positions));assert a['open_positions'][0]['floating_pnl']==15
 b=sync(tmp_path,envelope([entry],[dict(position_id='100',volume=1,floating_pnl=-7.5)]))
 assert b['open_positions'][0]['floating_pnl']==-7.5
 assert b['revision']==a['revision'] # Floating updates do not rebuild closed-trade reports.
 month=__import__('datetime').datetime.fromtimestamp(NOW,journaling.TZ).strftime('%Y-%m')
 assert journaling.snapshot(tmp_path/'db.sqlite3','mt5',month)['summary']['pnl']==0
 f=tmp_path/'export.json';f.write_text('{')
 stale=m.sync(tmp_path/'db.sqlite3',f,NOW+1)
 assert stale['state']=='unavailable' and stale['open_positions'][0]['floating_pnl']==-7.5

def test_account_balance_is_reported_not_reconstructed_from_ledger(tmp_path):
 d=envelope(account_balance=1234.56)
 r=sync(tmp_path,d)
 assert r['account_balance']==1234.56 and r['currency']=='USD' and r['closed_count']==0
 d['timestamp']+=1;d.pop('account_balance')
 f=tmp_path/'export.json';f.write_text(json.dumps(d))
 r=m.sync(tmp_path/'db.sqlite3',f,NOW+2)
 assert r['account_balance'] is None
 d['timestamp']+=1;d['account_balance']='1234'
 f.write_text(json.dumps(d));assert m.sync(tmp_path/'db.sqlite3',f,NOW+3)['state']=='unavailable'
