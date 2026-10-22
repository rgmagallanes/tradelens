"""One frozen opening-range experiment; no imports of execution services."""
import json,hashlib,math
from datetime import datetime,time,timedelta,timezone
from zoneinfo import ZoneInfo
from pathlib import Path
from collections import Counter
NY=ZoneInfo('America/New_York')

def simulate(bars):
    if len(bars)!=120 or any(bars[i]['time']-bars[i-1]['time']!=60 for i in range(1,120)):raise ValueError('Complete 120-minute session required')
    high=max(b['high'] for b in bars[:15]);low=min(b['low'] for b in bars[:15]);signal=None
    for j in range(15,120,5):
        close=bars[j+4]['close']
        if close>high or close<low:
            signal=(j+5,1 if close>high else -1);break
    if not signal:return None,'no_breakout'
    first,side=signal;level=high if side==1 else low
    for j in range(first,min(first+10,119)):
        b=bars[j]
        if side*(b['close']-level)<=0:return None,'retest_invalidated'
        if (b['low']<=level if side==1 else b['high']>=level) and side*(b['close']-b['open'])>0:
            entry=bars[j+1]['open'];stop=b['low']-.01 if side==1 else b['high']+.01;risk=side*(entry-stop)
            if risk<=0:return None,'invalid_entry_gap'
            target=entry+side*2*risk;exit=bars[-1]['close'];exit_time=bars[-1]['time']+60;reason='time_exit';ambiguous=False
            for e in bars[j+1:]:
                stop_hit=e['low']<=stop if side==1 else e['high']>=stop
                target_hit=e['high']>=target if side==1 else e['low']<=target
                if stop_hit:
                    exit=min(stop,e['open']) if side==1 else max(stop,e['open']);reason='stop';exit_time=e['time'];ambiguous=target_hit;break
                if target_hit:exit=target;reason='target';exit_time=e['time'];break
            return dict(side='buy' if side==1 else 'sell',range_high=high,range_low=low,breakout_known_at=bars[first-1]['time']+60,retest_known_at=b['time']+60,entry_time=bars[j+1]['time'],entry=entry,stop=stop,target=target,risk=risk,exit=exit,exit_bar_time=exit_time,exit_reason=reason,both_touched=ambiguous,gross=side*(exit-entry)),None
    return None,'retest_expired'

def metrics(trades,cost):
    net=[t['gross']-cost for t in trades];positive=sum(max(0,x) for x in net);negative=-sum(min(0,x) for x in net)
    equity=peak=drawdown=0
    for x in net:equity+=x;peak=max(peak,equity);drawdown=max(drawdown,peak-equity)
    return dict(trades=len(net),wins=sum(x>0 for x in net),win_rate=sum(x>0 for x in net)/len(net) if net else None,gross=sum(t['gross'] for t in trades),net=sum(net),profit_factor=positive/negative if negative else None,max_closed_drawdown=drawdown,mean_net_R=sum((t['gross']-cost)/t['risk'] for t in trades)/len(trades) if trades else None,ambiguous_stop_first=sum(t['both_touched'] for t in trades))

def run(input_path,output_path):
    from .history import read_history
    raw=Path(input_path).read_bytes();h=read_history(input_path,max_bars=200000)
    if h['state']!='valid' or h['data'].get('demo') is not True or h['data'].get('server_utc_offset_seconds')!=0:raise ValueError('Validated UTC+0 demo input required')
    series=[b for b in h['data']['candles']['M1'] if b['closed']];lookup={b['time']:b for b in series}
    first=datetime.fromtimestamp(series[0]['time'],NY).date();last=datetime.fromtimestamp(series[-1]['time'],NY).date();sessions=[];skipped=[];reasons=Counter();trades=[]
    for n in range((last-first).days+1):
        d=first+timedelta(days=n)
        if d.weekday()>=5:continue
        start=int(datetime.combine(d,time(9,30),NY).timestamp());times=list(range(start,start+7200,60))
        missing=sum(t not in lookup for t in times)
        if missing:skipped.append(dict(day=d.isoformat(),missing_minutes=missing));continue
        sessions.append(d.isoformat());trade,reason=simulate([lookup[t] for t in times])
        if trade:trades.append(dict(day=d.isoformat(),**trade))
        else:reasons[reason]+=1
    split=math.floor(len(sessions)*.7);cut=sessions[split] if split<len(sessions) else None
    result=dict(status='EXPLORATORY / UNPROVEN',symbol='BTCUSDm',spec_sha256=hashlib.sha256(Path('strategy/ny-opening-range-research-v1.md').read_bytes()).hexdigest(),source_sha256=hashlib.sha256(raw).hexdigest(),complete_sessions=len(sessions),sessions=sessions,skipped_sessions=skipped,no_trade_reasons=dict(reasons),later_segment_start=cut,normalization='USD price movement per 1 BTC exposure, not account returns',runs=[])
    for spread in [6.4,12.8]:
        cost=spread+2
        result['runs'].append(dict(spread=spread,slippage_per_side=1,roundtrip_cost=cost,all=metrics(trades,cost),early=metrics([t for t in trades if cut is None or t['day']<cut],cost),later=metrics([t for t in trades if cut is not None and t['day']>=cut],cost),trades=[dict(t,net=t['gross']-cost,net_R=(t['gross']-cost)/t['risk']) for t in trades]))
    Path(output_path).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');return result

if __name__=='__main__':
    result=run('research/exness-history-volume-2026-10-19.json','research/ny-opening-range-v1-2026-10-21.json')
    print(json.dumps({k:v for k,v in result.items() if k not in ('sessions','runs')},indent=2))
    for r in result['runs']:print(json.dumps({k:v for k,v in r.items() if k!='trades'},indent=2))
