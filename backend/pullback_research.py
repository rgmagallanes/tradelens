"""Fixed v3 trend-pullback candle experiment. No live state imports or writes."""
from collections import Counter
from .auto_research import trend,fill_plan,exit_fill


def contiguous_tail(bars,dt):
    start=0
    for i in range(1,len(bars)):
        if bars[i]['time']-bars[i-1]['time']!=dt:start=i
    return bars[start:]


def swings(bars):
    bars=contiguous_tail(bars[-96:],300);out=[]
    for i in range(2,len(bars)-2):
        b=bars[i];window=bars[i-2:i+3]
        for kind,key in [('high','high'),('low','low')]:
            if all(b[key]>x[key] if kind=='high' else b[key]<x[key] for j,x in enumerate(window) if j!=2):
                out.append(dict(kind=kind,price=b[key],time=b['time'],known=bars[i+2]['time']+300))
    return out


def setup(m5,m1,h1,long,used):
    """Returns activation using no pivot learned during the touch candle."""
    if len(m5)<6 or len(m1)<3 or not trend(h1,900,long):return None,None
    b=m5[-1];known=[s for s in swings(m5[:-1]) if s['known']<=b['time']]
    highs=[s for s in known if s['kind']=='high'];lows=[s for s in known if s['kind']=='low']
    if len(highs)<2 or len(lows)<2:return None,None
    sign=1 if long else -1
    if not (sign*(highs[-1]['price']-highs[-2]['price'])>0 and sign*(lows[-1]['price']-lows[-2]['price'])>0):return None,None
    swing=lows[-1] if long else highs[-1];key=(long,swing['time']);L=swing['price'];d=L*.0005
    if key in used:return None,None
    held=b['low']>=L-d and b['close']>=L if long else b['high']<=L+d and b['close']<=L
    if not (b['low']<=L+d and b['high']>=L-d and held):return None,None
    used.add(key)
    targets=[s for s in (highs if long else lows) if (s['price']>b['close'] if long else s['price']<b['close'])]
    if not targets:return None,'NO_TARGET'
    recent=m1[-3:]
    if any(y['time']-x['time']!=60 for x,y in zip(recent,recent[1:])):return None,'ENTRY_DATA_GAP'
    target=min(targets,key=lambda s:abs(s['price']-b['close']))
    return dict(id=f"{'long' if long else 'short'}-{swing['time']}",side='resistance' if long else 'support',price=L,created=b['time']+300,touch=b['time'],swing=swing,target=target['price'],target_evidence=target,threshold=max(x['high'] for x in recent) if long else min(x['low'] for x in recent),extreme=b['low'] if long else b['high'],count=0,state='WAITING'),None


def confirmation(s,b):
    long=s['side']=='resistance';L=s['price'];d=L*.0005
    s['count']+=1
    if s['count']>6:return 'EXPIRED'
    invalid=b['low']<L-d or b['close']<L if long else b['high']>L+d or b['close']>L
    if invalid:return 'INVALIDATED'
    s['extreme']=min(s['extreme'],b['low']) if long else max(s['extreme'],b['high'])
    confirms=b['close']>s['threshold'] and b['close']>b['open'] if long else b['close']<s['threshold'] and b['close']<b['open']
    return 'CONFIRMED' if confirms else 'WAITING'


def run(data,spread=6.4,days=7,end=None):
    series=data['candles'];entry=[b for b in series['M1'] if b['closed']]
    if not entry:return dict(status='BLOCKED',reason='No M1 history')
    end=entry[-1]['time']+60 if end is None else end;start=end-days*86400;split=end-2*86400
    if entry[0]['time']>start or entry[-1]['time']+60<end:return dict(status='BLOCKED',reason='Incomplete M1 window')
    if not series['M5'] or series['M5'][0]['time']>start-96*300 or not series['M15'] or series['M15'][0]['time']>start-60*900:return dict(status='BLOCKED',reason='Insufficient warmup')
    bars=[b for b in entry if start<=b['time'] and b['time']+60<=end]
    equity=1000.;peak=1000.;dd=0.;negative=0.;streak=0;paused=False;paused_at=None;position=None;uncertain=None;attempts=[];trades=[];skips=Counter();used=set();previous=None;last_m5=None;gaps=[]
    def close(p,fill,reason,amb,b):
        nonlocal equity,peak,dd,negative,streak,paused,paused_at
        pnl=(fill-p['entry'])*(1 if p['long'] else -1)*p['lots'];equity+=pnl;peak=max(peak,equity);dd=max(dd,peak-equity);negative+=max(0,-pnl);streak=streak+1 if pnl<0 else 0
        trades.append(dict(p,exit=fill,exit_bar=b['time'],reason=reason,ambiguous=amb,pnl=pnl,modeled_cost=(spread+10)*p['lots'],segment='final_two_days' if p['entered']>=split else 'first_five_days'))
        if negative>=20 or streak>=3:paused=True;paused_at=b['time']
    for i,b in enumerate(bars):
        now=b['time']+60
        if previous and b['time']!=previous['time']+60:
            gaps.append(dict(after=previous['time'],before=b['time']))
            for s in attempts:
                if s['state'] in ('WAITING','PENDING'):s['state']='DATA_GAP';skips['DATA_GAP']+=1
            if position:uncertain=dict(position,gap=gaps[-1]);position=None;break
        was_position=position is not None
        if position:
            if b['time']>=position['deadline']:fill=b['open']+(0 if position['long'] else spread)+(-5 if position['long'] else 5);reason='TIME';amb=False
            else:fill,reason,amb=exit_fill(position,b,spread)
            if fill is not None:close(position,fill,reason,amb,b);position=None
        for s in attempts:
            if s['state']!='PENDING':continue
            s['state']='CONSUMED'
            if b['time']!=s['confirmation']+60:skips['MISSED_ENTRY']+=1;continue
            if paused or was_position or position:skips['RISK_OR_POSITION']+=1;continue
            h=[x for x in series['M15'] if x['closed'] and x['time']+900<=b['time']]
            if not trend(h,900,s['side']=='resistance'):skips['ENTRY_CONTEXT_FAILED']+=1;continue
            p,reason=fill_plan(s,b,spread,equity)
            if reason:skips[reason]+=1;continue
            p.update(pullback=s['touch'],confirmation=s['confirmation'],swing=s['swing'],target_evidence=s['target_evidence']);position=p
            fill,reason,amb=exit_fill(p,b,spread)
            if fill is not None:close(p,fill,reason,amb,b);position=None
            break
        h=[x for x in series['M15'] if x['closed'] and x['time']+900<=now]
        for s in attempts:
            if s['state']!='WAITING' or b['time']<s['created']:continue
            if paused:s['state']='RISK_PAUSED';continue
            result=confirmation(s,b)
            if result=='CONFIRMED':
                if trend(h,900,s['side']=='resistance'):s.update(state='PENDING',confirmation=b['time'])
                else:s['state']='CONTEXT_FAILED';skips['CONFIRM_CONTEXT_FAILED']+=1
            elif result!='WAITING':s['state']=result;skips[result]+=1
        m5=[x for x in series['M5'] if x['closed'] and x['time']+300<=now]
        if not paused and m5 and m5[-1]['time']!=last_m5:
            # Skip stale M5 bars whose expected close has already passed.
            if m5[-1]['time']+300==now:
                for long in (True,False):
                    s,reason=setup(m5,bars[max(0,i-2):i+1],h,long,used)
                    if reason:skips[reason]+=1
                    if s:attempts.append(s)
            last_m5=m5[-1]['time']
        previous=b
    segments={}
    for name in ('first_five_days','final_two_days'):
        ts=[t for t in trades if t['segment']==name];segments[name]=dict(closed_trades=len(ts),net_pnl=round(sum(t['pnl'] for t in ts),4),win_rate=sum(t['pnl']>0 for t in ts)/len(ts) if ts else None)
    return dict(status='UNPROVEN / MODELED / MARGIN UNVERIFIED',variant='trend_pullback_v3',period=dict(start=start,end=end,segment_split=split,bars=len(bars)),spread_assumption=spread,attempts=len(attempts),skips=dict(skips),closed_trades=len(trades),net_pnl=round(equity-1000,4),modeled_costs=round(sum(t['modeled_cost'] for t in trades),4),realized_drawdown=round(dd,4),ambiguous=sum(t['ambiguous'] for t in trades),segments=segments,risk_paused=paused,paused_at=paused_at,gaps=gaps,uncertain_position=uncertain,open_position=position,trades=trades,setups=attempts)
