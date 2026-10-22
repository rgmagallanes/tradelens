import copy,json,sqlite3
import pytest
from backend import engine as e
from backend.paper_service import PaperService

def bar(t,o=10000,h=10015,l=9990,c=10010,closed=True):return dict(time=t,open=o,high=h,low=l,close=c,closed=closed)
def quote(t=2700000):return dict(tick_time_msc=t,bid=10008,ask=10010,chart_basis='bid',currency='USD',tick_size=.01,contract_size=1,volume_min=.01,volume_max=100,volume_step=.01,margin_buy_per_lot=100,margin_sell_per_lot=100)
def configured():
 s=e.initial();s.update(enabled=True,recovering=False,recovery=2,last_bar=2100,last_poll=999)
 s['config']=dict(parity_verified=True,verification_note='fixture completed OHLC parity',commission_confirmed=True,commission_per_lot_side=0,commission_source='fixture zero fee')
 return s
def level(price=10000,side='resistance',created=900):return dict(id=str(price),price=price,side=side,created=created,expires=created+86400,state='ARMED',context_reviewed=True,evidence=[])
def data(last,long=True):
 h1=[bar(0,h=10000,l=9990,c=9995),bar(3600,o=10000,h=10040,l=9990,c=10030)] if long else [bar(0,h=10010,l=10000,c=10005),bar(3600,o=10000,h=10010,l=9960,c=9970)]
 return {'M5':last,'H1':h1}
def opened(long=True):
 s=configured();s['levels']=[level(side='resistance' if long else 'support'),level(10100 if long else 9900,side='resistance' if long else 'support')]
 prev=bar(2100,c=10000);br=bar(2400,c=10010 if long else 9990)
 q=quote();q.update(bid=10008 if long else 9992,ask=10010 if long else 9994)
 e.step(s,data([prev,br],long),q,1000)
 assert s['levels'][0]['state']=='BREAKOUT_CONFIRMED'
 retest=bar(2700,o=10002 if long else 9998,h=10010 if long else 10000,l=10000 if long else 9990,c=10008 if long else 9992)
 q['tick_time_msc']=3000000;e.step(s,data([prev,br,retest],long),q,1002)
 assert s['levels'][0]['state']=='ENTRY_ELIGIBLE'
 q['tick_time_msc']=3001000;e.step(s,data([prev,br,retest],long),q,1004,monotonic_now=50,run_id='test')
 assert s['position'];return s,q,[prev,br,retest]

@pytest.mark.parametrize('long',[True,False])
def test_long_short_full_flow_and_idempotent_exit(long):
 s,q,bars=opened(long);p=s['position'];assert p['modeled_loss']<=5 and p['rr']>=2
 assert p['deadline_monotonic']==1850
 q.update(tick_time_msc=3002000,bid=p['target']+10,ask=p['target']+12) if long else q.update(tick_time_msc=3002000,bid=p['target']-12,ask=p['target']-10)
 e.step(s,data(bars,long),q,1006,monotonic_now=52,run_id='test')
 assert s['position'] is None and len(s['closed'])==1 and s['closed'][0]['exit_reason']=='TARGET'
 e.step(s,data(bars,long),q,1007);assert len(s['closed'])==1

@pytest.mark.parametrize('long',[True,False])
def test_gap_stop_adverse_fill(long):
 s,q,bars=opened(long);p=copy.deepcopy(s['position']);q.update(tick_time_msc=3002000)
 if long:q.update(bid=p['stop']-20,ask=p['stop']-18)
 else:q.update(bid=p['stop']+18,ask=p['stop']+20)
 e.step(s,data(bars,long),q,1006)
 close=s['closed'][0];assert close['exit_reason']=='STOP'
 assert close['exit']==(p['stop']-25 if long else p['stop']+25)
 assert close['pnl']<-p['risk_budget'] # gaps can exceed planned risk

def test_no_same_snapshot_entry_and_late_quote():
 s,q,bars=opened();s['position']=None;l=s['levels'][0];l['state']='ENTRY_ELIGIBLE';q['tick_time_msc']=l['confirmation_quote']
 e.step(s,data(bars),q,1005);assert s['position'] is None
 q['tick_time_msc']+=1;e.step(s,data(bars),q,1013);assert l['state']=='MISSED_ENTRY'

def test_forming_and_equality_do_not_breakout():
 s=configured();s['levels']=[level()];q=quote();before=bar(2100,c=10000)
 e.step(s,data([before,bar(2400,c=10020,closed=False)]),q,1000);assert s['levels'][0]['state']=='ARMED'
 e.step(s,data([before,bar(2400,c=10005)]),q,1002);assert s['levels'][0]['state']=='ARMED'

def test_invalid_retest_and_six_bar_expiry():
 s=configured();s['levels']=[level()];q=quote();bars=[bar(2100,c=10000),bar(2400,c=10010)]
 e.step(s,data(bars),q,1000);bars.append(bar(2700,l=9994,c=10008));e.step(s,data(bars),q,1002);assert s['levels'][0]['state']=='INVALIDATED'
 s=configured();s['levels']=[level()];bars=[bar(2100,c=10000),bar(2400,c=10010)];e.step(s,data(bars),q,1000)
 for i in range(1,8):
  bars.append(bar(2400+i*300,o=10004,h=10010,l=10000,c=10003));q['tick_time_msc']+=1;e.step(s,data(bars),q,1000+2*i)
 assert s['levels'][0]['state']=='EXPIRED'

def test_evidence_no_future_and_spacing():
 bars=[bar(i*900,o=10000,h=10001,l=9999,c=10000) for i in range(8)]
 bars[1]=bar(900,h=10000,l=9980,c=9989);bars[4]=bar(3600,h=10000,l=9980,c=9989)
 candidates=e.evidence(bars,10000,'resistance');assert 0 in [c['time'] for c in candidates]
 assert 7*900 not in [c['time'] for c in candidates]
 s=e.initial();l=e.register(s,10000,'resistance',[0,2700],bars,1000,True);assert len(l['evidence'])==2
 with pytest.raises(ValueError):e.register(s,10000,'resistance',[0,1800],bars,1000,True)

def test_data_gap_recovery_and_cancel():
 s=configured();s['levels']=[level()];q=quote();e.step(s,data([bar(2100),bar(2400)]),q,1000,False)
 assert s['levels'][0]['state']=='STALE_FEED' and s['recovering']
 e.step(s,data([bar(2400),bar(2700)]),q,1002);assert s['recovery']==1
 e.step(s,data([bar(2700),bar(3000)]),q,1004);assert not s['recovering']

def test_costs_and_step_rounding_no_extra_spread():
 s,q,bars=opened();p=s['position'];assert p['entry']==10015 # ask + 5, no extra spread deduction
 assert p['modeled_loss']==pytest.approx((10015-9997.5+5)*p['lots'])
 assert p['lots']==.22
 l=s['levels'][0];q['volume_min']=10
 assert e.sized_plan(s,l,q,1004)[1]=='SIZE_FAILED'

def test_news_pause_and_risk_restart_persist(tmp_path):
 s=configured();s['news_pause']=True;s['levels']=[level()];e.step(s,data([bar(2100),bar(2400)]),quote(),1000);assert s['levels'][0]['state']=='ARMED'
 now=__import__('time').time();s['closed']=[dict(pnl=-7,closed_at=now) for _ in range(3)]
 assert e.risk_gate(s,now);assert s['needs_resume']
 service=PaperService(tmp_path/'paper.sqlite3',tmp_path/'quote.json',lambda:{})
 service.mutate(lambda state:state.update(s));service.restart()
 status=service.mutate(lambda state:None);assert status['needs_resume'] and status['pause_date']==e.day(now)
 with pytest.raises(ValueError):service.control('resume')

def test_time_exit_monotonic_not_wall_and_stale():
 s,q,bars=opened();q['tick_time_msc']+=1
 e.step(s,data(bars),q,1006,monotonic_now=1850,run_id='test');assert s['closed'][0]['exit_reason']=='TIME'
 s,q,bars=opened();e.step(s,data(bars),q,1006,False);assert s['position']['uncertainty'] and not s['closed']

def test_missing_prerequisites_and_no_target():
 assert e.prerequisites({},quote())
 s,q,bars=opened();s['levels']=s['levels'][:1];assert e.sized_plan(s,s['levels'][0],q,1004)[1]=='NO_TARGET'

def test_ambiguous_replay_is_stop_first():
 assert e.candle_replay_exit(bar(0,h=10200,l=9800),9900,10100,True)==dict(reason='STOP',ambiguous=True)
 assert e.integrity()

def test_h1_gap_and_postbreakout_target_rejected():
 s,q,bars=opened();h1=data(bars)['H1'];h1[-1]['time']=7200;assert not e.context(h1,True)
 s['levels'][1]['registered_broker_tick']=(s['levels'][0]['breakout_bar']['time']+300)*1000+1
 assert e.sized_plan(s,s['levels'][0],q,1004)[1]=='NO_TARGET'

def test_unknown_fees_and_broker_specs_block_start(tmp_path):
 q=quote();q.pop('tick_size');assert 'Missing broker specification: tick_size' in e.prerequisites(configured()['config'],q)
 service=PaperService(tmp_path/'paper.sqlite3',tmp_path/'quote.json',lambda:{})
 with pytest.raises(ValueError):service.control('start')
 assert service.mutate(lambda s:None)['enabled'] is False

def test_atomic_audit_and_cancel(tmp_path):
 service=PaperService(tmp_path/'paper.sqlite3',tmp_path/'quote.json',lambda:{})
 service.mutate(lambda s:s['levels'].append(level()))
 service.cancel('10000')
 with pytest.raises(ValueError):service.cancel('10000')
 with service.connection() as c:
  rows=c.execute("SELECT COUNT(*) FROM paper_audit WHERE kind='USER_CANCELLED'").fetchone()[0]
 assert rows==1

def test_margin_helper_freshness_and_validation(tmp_path):
 from backend.paper_service import read_margin
 p=tmp_path/'margin.json';q=quote();d=dict(version=1,timestamp=999,symbol='BTCUSDm',currency='USD',demo=True,terminal_connected=True,bid=q['bid'],ask=q['ask'],margin_buy_per_lot=100,margin_sell_per_lot=101)
 p.write_text(json.dumps(d));assert read_margin(p,q,1000)['margin_buy_per_lot']==100
 assert read_margin(p,q,1020)=={}
 d['demo']=False;p.write_text(json.dumps(d));assert read_margin(p,q,1000)=={}
 d.update(demo=True,margin_buy_per_lot=-1);p.write_text(json.dumps(d));assert read_margin(p,q,1000)=={}
 p.write_text('{');assert read_margin(p,q,1000)=={}
