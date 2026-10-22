import pytest
from backend.orb_research import simulate,metrics,NY
from datetime import datetime

def session():return [dict(time=i*60,open=100,high=101,low=99,close=100) for i in range(120)]
def setup(side=1):
 b=session()
 for i in range(15,20):b[i].update(open=101,high=104,low=101,close=103)
 b[20].update(open=101.5,high=103,low=100.5,close=102)
 for i in range(21,120):b[i].update(open=102,high=103,low=101,close=102)
 if side==-1:
  b=[dict(time=x['time'],open=200-x['open'],high=200-x['low'],low=200-x['high'],close=200-x['close']) for x in b]
 return b

def test_waits_for_closed_m5_then_next_open_and_time_exits():
 t,reason=simulate(setup());assert reason is None and t['entry_time']==21*60 and t['breakout_known_at']==20*60
 assert t['exit_reason']=='time_exit' and t['gross']==0

def test_short_is_symmetric_and_both_touches_stop_first():
 for side in [1,-1]:
  b=setup(side);b[21].update(high=110,low=90)
  t,_=simulate(b);assert t['both_touched'] and t['exit_reason']=='stop' and t['gross']<0

def test_no_same_candle_lookahead_and_invalid_retest():
 b=setup();b[19].update(low=100,close=103)
 t,_=simulate(b);assert t['retest_known_at']==21*60
 b[20]['close']=100
 assert simulate(b)==(None,'retest_invalidated')

def test_gaps_rejected_costs_and_dst():
 with pytest.raises(ValueError):simulate(session()[:-1])
 t,_=simulate(setup());assert metrics([t],8.4)['net']==-8.4
 assert datetime(2026,10,21,9,30,tzinfo=NY).utcoffset().total_seconds()==-14400
 assert datetime(2026,11,9,9,30,tzinfo=NY).utcoffset().total_seconds()==-18000
