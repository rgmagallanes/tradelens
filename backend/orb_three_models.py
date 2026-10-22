"""Three frozen OR models, causal signals and independent/combined allocation."""
from collections import Counter
from datetime import datetime,time,timedelta
from pathlib import Path
import hashlib,json,math
from .orb_research import NY,metrics
from .history import read_history
MODELS=('breakout','retest','reversal')

def validate_session(bars):
 if len(bars)!=120 or any(bars[i]['time']-bars[i-1]['time']!=60 for i in range(1,120)):raise ValueError('Complete 120-minute session required')

def events(bars,hi,lo):
 previous=0;out=[]
 for j in range(19,120,5):
  side=1 if bars[j]['close']>hi else -1 if bars[j]['close']<lo else 0
  if side and side!=previous:out.append((j,side))
  previous=side
 return out

def pivot(bars,j,side):
 for k in range(j-2,16,-1):
  key='high' if side==1 else 'low';v=bars[k][key]
  if all((v>bars[q][key] if side==1 else v<bars[q][key]) for q in range(k-2,k+3) if q!=k):return k,v
 return None

def candidates(bars):
 validate_session(bars);hi=max(b['high'] for b in bars[:15]);lo=min(b['low'] for b in bars[:15]);out=[];diagnostics=Counter()
 def add(model,j,side,stop,parent,evidence,target=None):
  if j>=119:diagnostics[model+':no_next_bar']+=1;return
  entry=bars[j+1]['open'];risk=side*(entry-stop)
  if risk<=0:diagnostics[model+':invalid_risk_gap']+=1;return
  target=entry+side*2*risk if target is None else target
  if side*(target-entry)<=0:diagnostics[model+':target_behind_entry']+=1;return
  out.append(dict(model=model,side='buy' if side==1 else 'sell',direction=side,signal_index=j,entry_index=j+1,entry_time=bars[j+1]['time'],signal_known_at=bars[j]['time']+60,parent_breakout_known_at=bars[parent]['time']+60,range_high=hi,range_low=lo,entry=entry,stop=stop,target=target,risk=risk,evidence=evidence))
 for parent,side in events(bars,hi,lo):
  level=hi if side==1 else lo;found=False
  for j in range(parent,min(parent+5,119)):
   a,b,c=bars[j-2:j+1]
   gap=c['low']>a['high'] if side==1 else c['high']<a['low']
   if gap and side*(b['close']-b['open'])>0 and side*(c['close']-level)>0:
    add('breakout',j,side,b['low']-.01 if side==1 else b['high']+.01,parent,dict(fvg_first_time=a['time'],fvg_middle_time=b['time'],fvg_third_time=c['time']));found=True;break
  if not found:diagnostics['breakout:no_gap_confirmation']+=1
  found=False
  for j in range(parent+1,min(parent+31,119)):
   b=bars[j]
   if (b['close']<=lo if side==1 else b['close']>=hi):diagnostics['retest:far_boundary_invalidated']+=1;found=True;break
   touch=b['low']<=level if side==1 else b['high']>=level
   if touch and side*(b['close']-level)>0 and side*(b['close']-b['open'])>0:
    add('retest',j,side,b['low']-.01 if side==1 else b['high']+.01,parent,dict(retest_time=b['time']));found=True;break
  if not found:diagnostics['retest:no_confirmation_in_window']+=1
  fail=next((j for j in range(parent+1,119) if side*(bars[j]['close']-level)<=0 and (bars[j]['close']>lo if side==1 else bars[j]['close']<hi)),None)
  if fail is None:diagnostics['reversal:no_failed_break']+=1;continue
  reverse=-side;bos=None
  for j in range(fail+1,min(fail+31,119)):
   swing=pivot(bars,j,reverse)
   if not swing:continue
   k,v=swing;b=bars[j];mean=sum(abs(x['close']-x['open']) for x in bars[j-10:j])/10
   if reverse*(bars[j-1]['close']-v)<=0 and reverse*(b['close']-v)>0 and reverse*(b['close']-b['open'])>mean:
    block=next((q for q in range(j-1,max(14,j-11),-1) if reverse*(bars[q]['close']-bars[q]['open'])<0),None)
    if block is not None:bos=(j,k,block);break
  if bos is None:diagnostics['reversal:no_structure_displacement']+=1;continue
  jbos,k,block=bos;zone=bars[block];found=False
  for j in range(jbos+1,min(jbos+31,119)):
   b=bars[j]
   if (b['close']<zone['low'] if reverse==1 else b['close']>zone['high']):diagnostics['reversal:zone_invalidated']+=1;found=True;break
   touch=b['low']<=zone['high'] and b['high']>=zone['low']
   if touch and reverse*(b['close']-b['open'])>0 and (b['close']>zone['high'] if reverse==1 else b['close']<zone['low']):
    stop=min(zone['low'],b['low'])-.01 if reverse==1 else max(zone['high'],b['high'])+.01
    target=max(x['high'] for x in bars[:j+1]) if reverse==1 else min(x['low'] for x in bars[:j+1])
    add('reversal',j,reverse,stop,parent,dict(failure_time=bars[fail]['time'],pivot_time=bars[k]['time'],pivot_known_at=bars[k+2]['time']+60,bos_time=bars[jbos]['time'],zone_time=zone['time'],zone_low=zone['low'],zone_high=zone['high'],target_known_at=b['time']+60),target);found=True;break
  if not found:diagnostics['reversal:no_zone_retest']+=1
 unique={}
 for c in sorted(out,key=lambda c:(c['entry_index'],MODELS.index(c['model']),c['parent_breakout_known_at'])):
  key=(c['model'],c['side'],c['entry_index'])
  if key in unique:diagnostics[c['model']+':duplicate_candidate']+=1
  else:unique[key]=c
 return list(unique.values()),dict(diagnostics)

def execute(bars,c):
 side=c['direction'];stop=c['stop'];target=c['target'];exit=bars[-1]['close'];last=119;reason='time_exit';amb=False
 for j in range(c['entry_index'],120):
  b=bars[j];s=b['low']<=stop if side==1 else b['high']>=stop;t=b['high']>=target if side==1 else b['low']<=target
  if s:exit=min(stop,b['open']) if side==1 else max(stop,b['open']);last=j;reason='stop';amb=t;break
  if t:exit=target;last=j;reason='target';break
 return dict(c,exit=exit,exit_index=last,exit_bar_time=bars[last]['time'],available_again_at=bars[last]['time']+60,exit_reason=reason,both_touched=amb,gross=side*(exit-c['entry']))

def allocate(bars,items,model):
 trades=[];skips=Counter();available=0
 for c in items:
  if model!='combined' and c['model']!=model:continue
  if c['entry_index']<available:skips['overlap']+=1;continue
  if len(trades)>=3:skips['daily_limit']+=1;continue
  t=execute(bars,c);trades.append(t);available=t['exit_index']+1
 return trades,dict(skips)

def run(input_path,output_path,expected_symbol="BTCUSDm",cost_scenarios=None,spec_path="strategy/ny-opening-range-three-models-v2.md",normalization="USD price movement per 1 BTC exposure per trade, not account returns"):
 if cost_scenarios is None:cost_scenarios=[(6.4,1),(12.8,1)]
 if not cost_scenarios or any(not all(isinstance(x,(float,int)) and math.isfinite(x) and x>=0 for x in pair) or len(pair)!=2 for pair in cost_scenarios):raise ValueError("Explicit nonnegative spread/slippage scenarios required")
 raw=Path(input_path).read_bytes();h=read_history(input_path,max_bars=200000,expected_symbol=expected_symbol)
 if h['state']!='valid' or h['data'].get('demo') is not True or h['data'].get('server_utc_offset_seconds')!=0:raise ValueError('Validated UTC+0 demo history required')
 series=[b for b in h['data']['candles']['M1'] if b['closed']];lookup={b['time']:b for b in series};first=datetime.fromtimestamp(series[0]['time'],NY).date();last=datetime.fromtimestamp(series[-1]['time'],NY).date()
 sessions=[];skipped=[];diagnostics=Counter();trades={m:[] for m in (*MODELS,'combined')};allocation={m:Counter() for m in trades};candidate_count=Counter();audit=[]
 for n in range((last-first).days+1):
  d=first+timedelta(days=n)
  if d.weekday()>=5:continue
  start=int(datetime.combine(d,time(9,30),NY).timestamp());times=list(range(start,start+7200,60));missing=sum(t not in lookup for t in times)
  if missing:skipped.append(dict(day=d.isoformat(),missing_minutes=missing));continue
  sessions.append(d.isoformat());bars=[lookup[t] for t in times];items,diag=candidates(bars);diagnostics.update(diag);candidate_count.update(c['model'] for c in items)
  audit.extend(dict(day=d.isoformat(),**c) for c in items)
  for m in trades:
   rows,counts=allocate(bars,items,m);trades[m].extend(dict(day=d.isoformat(),**t) for t in rows);allocation[m].update(counts)
 cut=sessions[math.floor(len(sessions)*.7)] if sessions else None
 result=dict(status='EXPLORATORY / UNPROVEN',symbol=expected_symbol,spec_path=spec_path,source_sha256=hashlib.sha256(raw).hexdigest(),spec_sha256=hashlib.sha256(Path(spec_path).read_bytes()).hexdigest(),sessions=sessions,complete_sessions=len(sessions),skipped_sessions=skipped,later_segment_start=cut,candidates_by_model=dict(candidate_count),candidate_diagnostics=dict(diagnostics),allocation_skips={m:dict(c) for m,c in allocation.items()},candidate_audit=audit,normalization=normalization,runs=[])
 for spread,slippage in cost_scenarios:
  for model,rows in trades.items():
   cost=spread+2*slippage;result['runs'].append(dict(model=model,spread=spread,slippage_per_side=slippage,roundtrip_cost=cost,all=metrics(rows,cost),early=metrics([t for t in rows if t['day']<cut],cost),later=metrics([t for t in rows if t['day']>=cut],cost),trades=[dict(t,net=t['gross']-cost,net_R=(t['gross']-cost)/t['risk']) for t in rows]))
 Path(output_path).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');return result

if __name__=='__main__':
 r=run('research/exness-history-volume-2026-10-19.json','research/ny-opening-range-three-models-v2-2026-10-21.json')
 print(json.dumps({k:v for k,v in r.items() if k not in ('runs','sessions','candidate_audit')},indent=2))
 for row in r['runs']:print(json.dumps({k:v for k,v in row.items() if k!='trades'},indent=2))
