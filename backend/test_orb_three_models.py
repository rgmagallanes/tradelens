from copy import deepcopy
import pytest
from backend.orb_three_models import candidates,events,execute,allocate,pivot

def base():return [dict(time=1790000000+i*60,open=100,high=101,low=99,close=100) for i in range(120)]
def mirror(bars):return [dict(time=b['time'],open=200-b['open'],high=200-b['low'],low=200-b['high'],close=200-b['close']) for b in bars]
def retest_fixture():
 b=base();b[19].update(open=100,high=104,low=99,close=103)
 b[20].update(open=102,high=103,low=100,close=100.5)
 b[21].update(open=100.5,high=103,low=100.4,close=102)
 b[22].update(open=102,high=103,low=101,close=102)
 return b

def test_later_breakouts_rearm_only_after_close_inside():
 b=base()
 for j,c in [(19,103),(24,104),(29,100),(34,98),(39,97),(44,103)]:b[j]['close']=c
 assert events(b,101,99)==[(19,1),(34,-1),(44,1)]

def test_retest_accepts_brief_inside_close_and_enters_next_open():
 for bars in [retest_fixture(),mirror(retest_fixture())]:
  items,_=candidates(bars);r=next(c for c in items if c['model']=='retest')
  assert r['signal_index']==21 and r['entry_index']==22
  assert r['signal_known_at']==r['entry_time'] and r['parent_breakout_known_at']<r['entry_time']

def test_breakout_gap_requires_closed_five_minute_confirmation():
 b=base();b[17].update(high=101,low=99);b[18].update(open=100,close=103,high=104,low=100)
 b[19].update(open=103,close=104,high=105,low=102);b[20].update(open=104,high=105,low=103,close=104)
 items,_=candidates(b);a=next(c for c in items if c['model']=='breakout')
 assert a['signal_index']==19 and a['entry_index']==20 and a['stop']==99.99
 b[19]['low']=100
 assert not any(c['model']=='breakout' and c['signal_index']==19 for c in candidates(b)[0])

def reversal_fixture():
 b=base();b[19].update(open=99,high=100,low=97,close=98)
 b[20].update(open=99,high=101.5,low=98.5,close=100)
 b[21].update(high=101.5)
 b[22].update(open=100,high=102,low=99,close=100)
 b[23].update(high=101.5);b[24].update(high=101.5)
 b[25].update(open=101,high=101.2,low=99,close=100)
 b[26].update(open=100,high=104,low=100,close=103)
 b[27].update(open=100.5,high=102.5,low=100,close=102)
 b[28].update(open=102,high=103,low=101,close=102)
 b[29].update(open=102,high=104,low=101,close=103)
 return b

def test_reversal_pivot_requires_right_bars_and_target_is_not_future_high():
 b=reversal_fixture();assert pivot(b,23,1) is None
 for bars in [b,mirror(b)]:
  items,_=candidates(bars);r=next(c for c in items if c['model']=='reversal')
  assert r['signal_index']==27 and r['entry_index']==28
  assert r['evidence']['pivot_time']==bars[22]['time']
  assert r['evidence']['pivot_known_at']==bars[24]['time']+60
  assert r['target']==(104 if r['side']=='buy' else 96)
 b[90]['high']=999
 r=next(c for c in candidates(b)[0] if c['model']=='reversal')
 assert r['target']==104

def test_signal_prefix_is_invariant_to_future_prices():
 b=reversal_fixture();before=[c for c in candidates(b)[0] if c['signal_index']<=27]
 changed=deepcopy(b)
 for bar in changed[29:]:bar.update(open=500,high=1000,low=400,close=700)
 after=[c for c in candidates(changed)[0] if c['signal_index']<=27]
 assert before==after

def test_allocation_prevents_overlap_including_exit_minute_and_limits_three():
 b=base()
 def c(j,model):return dict(model=model,direction=1,entry_index=j,entry=100,stop=99.5,target=101,risk=.5)
 items=[c(20,'breakout'),c(20,'retest'),c(21,'reversal'),c(22,'retest'),c(23,'breakout')]
 trades,skips=allocate(b,items,'combined')
 assert len(trades)==3 and skips=={'overlap':1,'daily_limit':1}
 assert all(t['exit_reason']=='stop' and t['both_touched'] for t in trades)
 assert [t['model'] for t in trades]==['breakout','reversal','retest']

def test_gap_stop_and_invalid_session():
 b=base();b[20].update(open=98,high=101,low=97)
 c=dict(direction=1,entry_index=20,entry=100,stop=99,target=102,risk=1)
 t=execute(b,c);assert t['exit']==98 and t['gross']==-2
 with pytest.raises(ValueError):candidates(b[:-1])
