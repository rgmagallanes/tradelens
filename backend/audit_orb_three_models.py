"""Independent checks of saved trade timestamps, evidence, fills, accounting and allocation."""
import json,hashlib,math
from pathlib import Path
from datetime import datetime,time
from .orb_research import NY

def audit(input_path="research/exness-history-volume-2026-10-19.json",result_path="research/ny-opening-range-three-models-v2-2026-10-21.json"):
 spec_default="strategy/ny-opening-range-three-models-v2.md"
 data=json.loads(Path(input_path).read_text());result=json.loads(Path(result_path).read_text());lookup={b['time']:b for b in data['candles']['M1'] if b['closed']};checked=0
 assert hashlib.sha256(Path(input_path).read_bytes()).hexdigest()==result['source_sha256']
 assert hashlib.sha256(Path(result.get('spec_path',spec_default)).read_bytes()).hexdigest()==result['spec_sha256']
 for r in result['runs']:
  last_exit={};perday={};net=0;gross=0
  for t in r['trades']:
   side=1 if t['side']=='buy' else -1;entrybar=lookup[t['entry_time']];signalbar=lookup[t['signal_known_at']-60]
   assert t['entry_time']==t['signal_known_at']>=t['parent_breakout_known_at']
   assert t['entry']==entrybar['open'] and t['risk']==side*(t['entry']-t['stop'])>0
   assert t['entry_time']>=last_exit.get(t['day'],0);last_exit[t['day']]=t['available_again_at'];perday[t['day']]=perday.get(t['day'],0)+1
   assert perday[t['day']]<=3
   start=int(datetime.combine(datetime.fromisoformat(t['day']).date(),time(9,30),NY).timestamp())
   assert t['range_high']==max(lookup[start+i*60]['high'] for i in range(15))
   assert t['range_low']==min(lookup[start+i*60]['low'] for i in range(15))
   breakoutbar=lookup[t['parent_breakout_known_at']-60]
   breakside=side if t['model']!='reversal' else -side
   assert breakoutbar['close']>t['range_high'] if breakside==1 else breakoutbar['close']<t['range_low']
   ev=t['evidence']
   if t['model']=='breakout':
    a=lookup[ev['fvg_first_time']];b=lookup[ev['fvg_middle_time']];c=lookup[ev['fvg_third_time']]
    assert c['time']+60==t['signal_known_at']
    assert c['low']>a['high'] if side==1 else c['high']<a['low']
    assert side*(b['close']-b['open'])>0
    assert t['stop']==(b['low']-.01 if side==1 else b['high']+.01)
   elif t['model']=='retest':
    level=t['range_high'] if side==1 else t['range_low']
    assert signalbar['low']<=level if side==1 else signalbar['high']>=level
    assert side*(signalbar['close']-level)>0 and side*(signalbar['close']-signalbar['open'])>0
   else:
    assert ev['pivot_known_at']<=ev['bos_time']+60<t['signal_known_at']
    assert ev['failure_time']>=t['parent_breakout_known_at']
    pivotbar=lookup[ev['pivot_time']];key='high' if side==1 else 'low'
    assert all((pivotbar[key]>lookup[ev['pivot_time']+i*60][key] if side==1 else pivotbar[key]<lookup[ev['pivot_time']+i*60][key]) for i in [-2,-1,1,2])
    known=[lookup[x] for x in range(start,t['signal_known_at'],60)]
    assert t['target']==(max(b['high'] for b in known) if side==1 else min(b['low'] for b in known))
   if t['model']!='reversal':assert math.isclose(side*(t['target']-t['entry']),2*t['risk'],abs_tol=1e-7)
   expected_exit=lookup[start+119*60]['close'];expected_reason='time_exit';expected_time=start+119*60
   for stamp in range(t['entry_time'],start+7200,60):
    b=lookup[stamp];s=b['low']<=t['stop'] if side==1 else b['high']>=t['stop'];hit=b['high']>=t['target'] if side==1 else b['low']<=t['target']
    if s:expected_exit=min(t['stop'],b['open']) if side==1 else max(t['stop'],b['open']);expected_reason='stop';expected_time=stamp;break
    if hit:expected_exit=t['target'];expected_reason='target';expected_time=stamp;break
   assert expected_exit==t['exit'] and expected_reason==t['exit_reason'] and expected_time==t['exit_bar_time']
   movement=side*(t['exit']-t['entry']);cost=r['spread']+2*r.get('slippage_per_side',1)
   assert math.isclose(t['gross'],movement) and math.isclose(t['net'],movement-cost) and math.isclose(t['net_R'],(movement-cost)/t['risk'])
   net+=t['net'];gross+=t['gross'];checked+=1
  assert math.isclose(net,r['all']['net'],abs_tol=1e-7) and math.isclose(gross,r['all']['gross'],abs_tol=1e-7)
  assert r['all']['trades']==r['early']['trades']+r['later']['trades']
 for model in ['breakout','retest','reversal','combined']:
  a,b=[r for r in result['runs'] if r['model']==model]
  assert [(t['day'],t['entry_time'],t['exit'],t['model']) for t in a['trades']]==[(t['day'],t['entry_time'],t['exit'],t['model']) for t in b['trades']]
 return dict(status='passed',trade_scenario_rows_checked=checked,scenarios=len(result['runs']),checks=['source/spec hashes','M5 confirmation and next-M1 entry','opening range boundaries','FVG or retest evidence','confirmed reversal pivots and causal day-high/low target','independent exit scan','cost/R reconciliation','no overlap and daily cap','identical trade sets across cost scenarios','chronological split counts'])
if __name__=='__main__':
 report=audit();Path('research/ny-opening-range-three-models-v2-audit-2026-10-21.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
