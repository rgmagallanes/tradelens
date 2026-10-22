"""Exploratory setup-only replay. Never writes paper state or models unobserved fills."""
import argparse, hashlib, json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from .engine import P, context, evidence
from .history import read_history

LEVELS=[(82850,'resistance'),(82600,'support'),(82400,'support'),(82250,'support')]
def clock(t):
    return datetime.fromtimestamp(t,timezone.utc).strftime('%Y-%m-%d %H:%M')
def run(data,levels=LEVELS,start=None,end=None):
    series=data['candles']; m5=[b for b in series['M5'] if b['closed'] and (start is None or b['time']>=start) and (end is None or b['time']+300<=end)]; records=[]
    for price,side in levels:
        long=side=='resistance'; delta=price*P['tolerance_fraction']; state='WAITING_EVIDENCE'; record={'price':price,'side':side}; post=[]; previous=None
        for b in m5:
            now=b['time']+300
            m15=[x for x in series['M15'] if x['closed'] and x['time']+900<=now]
            h1=[x for x in series['H1'] if x['closed'] and x['time']+3600<=now]
            if state=='WAITING_EVIDENCE':
                chosen=[]
                for e in evidence(m15,price,side):
                    if not chosen or e['index']-chosen[-1]['index']>=3: chosen.append(e)
                if len(chosen)>=2:
                    state='ARMED';record.update(registered=clock(now),registered_time=now,evidence=[clock(e['time']) for e in chosen[:2]])
                previous=b;continue
            if now-record['registered_time']>=P['level_lifetime_seconds']:
                state='EXPIRED';break
            if previous is None or b['time']-previous['time']!=300:
                state='DATA_GAP';break
            if state=='ARMED':
                broken=(b['close']>price+delta and previous['close']<=price+delta) if long else (b['close']<price-delta and previous['close']>=price-delta)
                if broken:
                    record['breakout']=clock(b['time'])
                    if not context(h1,long):state='CONTEXT_FAILED';break
                    state='BREAKOUT_CONFIRMED';record['h1_context']=[clock(x['time']) for x in h1[-2:]]
            else:
                post.append(b)
                if len(post)>P['retest_bars']:state='EXPIRED';break
                invalid=(b['low']<price-delta or b['close']<price) if long else (b['high']>price+delta or b['close']>price)
                if invalid:state='INVALIDATED';break
                if b['low']<=price+delta and b['high']>=price-delta:state='RETEST_SEEN'
                confirm=(b['close']>price+delta and b['close']>b['open']) if long else (b['close']<price-delta and b['close']<b['open'])
                if state=='RETEST_SEEN' and confirm:
                    state='CONFIRMED_SETUP_ONLY';record['confirmation']=clock(b['time']);break
            previous=b
        record['outcome']=state;records.append(record)
    return {'status':'EXPLORATORY / UNPROVEN / NO FILL SIMULATION','clock':'MT5 broker-server',
        'period':{'first_m5':clock(m5[0]['time']) if m5 else None,'last_m5':clock(m5[-1]['time']) if m5 else None,'closed_m5_bars':len(m5),'m5_gaps':sum(b['time']-a['time']!=300 for a,b in zip(m5,m5[1:]))},
        'method':'One attempt per fixed level; register only after two fully known M15 reactions; closed H1/M15 data revealed by close time; M5 only thereafter; no automatic rearming.',
        'limitations':['Levels selected after viewing this history: selection bias remains despite chronological evidence checks.','Historical manual news/context review is unavailable and assumed clear for this diagnostic.','No historical executable bid/ask quotes, receipt latency or margin history: entries, costs, P/L, drawdown and win rate are NOT computed.','This is a setup diagnostic, not a complete frozen-v1 execution backtest.'],
        'counts':dict(Counter(r['outcome'] for r in records)),'levels':records}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--days',type=int);args=parser.parse_args()
    snapshot=args.input.read_bytes(); h=read_history(args.input,max_bars=10000)
    if h['state']!='valid':raise SystemExit('Invalid history; replay aborted')
    end=max(b['time']+300 for b in h['data']['candles']['M5'] if b['closed']);start=end-args.days*86400 if args.days else None
    report=run(h['data'],start=start,end=end);report['requested_days']=args.days;report['source_sha256']=hashlib.sha256(snapshot).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()
