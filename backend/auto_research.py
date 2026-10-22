"""Causal candle-only automatic-level candidates, isolated from live paper state."""
import hashlib,json,math
from collections import Counter
from .engine import round_tick

INTERVAL={'M1':60,'M5':300,'M15':900,'H1':3600}
VARIANTS={'lower':('M5','M1','M15'),'reference':('M15','M5','H1')}

def trend(bars,interval,long):
    bars=bars[-60:]
    if len(bars)<40 or any(b['time']-a['time']!=interval for a,b in zip(bars,bars[1:])):return False
    ema=bars[0]['close'];previous=ema
    for b in bars[1:]:previous=ema;ema+=2/21*(b['close']-ema)
    return bars[-1]['close']>ema and ema>previous if long else bars[-1]['close']<ema and ema<previous

def pivots(bars):
    bars=bars[-96:];out=[]
    for i in range(2,len(bars)-2):
        w=bars[i-2:i+3];b=bars[i]
        if any(y['time']-x['time']!=bars[1]['time']-bars[0]['time'] for x,y in zip(w,w[1:])):continue
        for side,key in [('resistance','high'),('support','low')]:
            price=b[key];d=price*.0005
            strict=all(price>x[key] if side=='resistance' else price<x[key] for j,x in enumerate(w) if j!=2)
            reacts=any(x['close']<=price-2*d if side=='resistance' else x['close']>=price+2*d for x in bars[i+1:i+4])
            if strict and reacts:out.append(dict(side=side,price=price,time=b['time'],index=i))
    return out

def add_levels(bars,now,levels,used):
    points=pivots(bars)
    for i,a in enumerate(points):
        if any(l['side']==a['side'] and now<l['expires'] and l['state']=='ARMED' and abs(l['price']-a['price'])<=a['price']*.0005 for l in levels):continue
        for b in points[i+1:]:
            if b['side']!=a['side'] or b['index']-a['index']<3 or abs(a['price']-b['price'])>a['price']*.0005:continue
            key=(a['side'],a['time'],b['time'])
            # Both pivots must independently react from the fixed first-pivot price.
            selected=[x for x in bars if x['time']==b['time']]
            following=[x for x in bars if b['time']<x['time']<=b['time']+3*(bars[1]['time']-bars[0]['time'])]
            if not selected or (selected[0]['close']>a['price'] if a['side']=='resistance' else selected[0]['close']<a['price']) or not any(x['close']<=a['price']*(1-.001) if a['side']=='resistance' else x['close']>=a['price']*(1+.001) for x in following):continue
            if key in used or any(l['side']==a['side'] and abs(l['price']-a['price'])<=a['price']*.0005 and b['time']<=l['evidence'][1] for l in levels):continue
            levels.append(dict(id=len(levels),side=a['side'],price=a['price'],evidence=[a['time'],b['time']],created=now,expires=now+86400,state='ARMED'))
            used.add(key);break

def fill_plan(level,b,spread,equity):
    long=level['side']=='resistance';sign=1 if long else -1
    entry=b['open']+(spread if long else 0)+sign*5
    stop=round_tick(level['extreme']-sign*level['price']*.00025,.01,up=not long)
    target=round_tick(level['target'],.01,up=not long)
    loss=sign*(entry-stop)+5;gain=sign*(target-entry)-5
    if loss<=0 or gain/loss<2:return None,'COST_FAILED'
    lots=math.floor((min(5,equity*.005)/loss)/.01+1e-9)*.01
    if lots<.01 or lots>200:return None,'SIZE_FAILED'
    return dict(long=long,entry=entry,stop=stop,target=target,lots=round(lots,2),entered=b['time'],deadline=b['time']+1800,level_id=level['id'],net_rr=gain/loss),None

def exit_fill(p,b,spread):
    long=p['long'];s=1 if long else -1;adjust=0 if long else spread
    low=b['low']+adjust;high=b['high']+adjust;op=b['open']+adjust
    hit_stop=low<=p['stop'] if long else high>=p['stop'];hit_target=high>=p['target'] if long else low<=p['target']
    if hit_stop:return (min(op,p['stop']) if long else max(op,p['stop']))-s*5,'STOP',hit_target
    if hit_target:return p['target']-s*5,'TARGET',False
    return None,None,False

def run(data,variant='lower',spread=6.4,days=7,end=None):
    ltf,etf,ctf=VARIANTS[variant];dt=INTERVAL[etf];series=data['candles']
    entrybars=[b for b in series[etf] if b['closed']]
    if not entrybars:return {'status':'BLOCKED','reason':'No '+etf+' history'}
    end=entrybars[-1]['time']+dt if end is None else end;start=end-days*86400;split=end-2*86400
    if entrybars[0]['time']>start or entrybars[-1]['time']+dt<end:return {'status':'BLOCKED','reason':'Incomplete requested '+etf+' window','available_bars':len(entrybars),'required_start':start,'first_available':entrybars[0]['time']}
    if any(not series[tf] or series[tf][0]['time']>start-96*INTERVAL[ltf] for tf in [ltf]):return {'status':'BLOCKED','reason':'Insufficient level warmup'}
    if not series[ctf] or series[ctf][0]['time']>start-60*INTERVAL[ctf]:return {'status':'BLOCKED','reason':'Insufficient context warmup'}
    bars=[b for b in entrybars if b['time']>=start and b['time']+dt<=end];levels=[];used=set();trades=[];skips=Counter();position=None;previous=None;equity=1000.;peak=1000.;dd=0.;negative=0.;streak=0;paused=False;lastmap=None;gaps=[];uncertain=None
    for b in bars:
        now=b['time']+dt
        if previous and b['time']!=previous['time']+dt:
            gaps.append({'after':previous['time'],'before':b['time']})
            for l in levels:
                if l['state'] in ('ARMED','BREAKOUT','RETEST','PENDING'):l['state']='DATA_GAP';skips['DATA_GAP']+=1
            if position:uncertain=dict(position,gap=gaps[-1]);position=None;break
        h=[x for x in series[ctf] if x['closed'] and x['time']+INTERVAL[ctf]<=now]
        was_position=position is not None
        if position:
            if b['time']>=position['deadline']:
                fill=b['open']+(0 if position['long'] else spread)+(-5 if position['long'] else 5);reason='TIME';amb=False
            else:fill,reason,amb=exit_fill(position,b,spread)
            if fill is not None:
                pnl=(fill-position['entry'])*(1 if position['long'] else -1)*position['lots'];equity+=pnl;peak=max(peak,equity);dd=max(dd,peak-equity);negative+=max(0,-pnl);streak=streak+1 if pnl<0 else 0
                trades.append(dict(position,exit=fill,exit_bar=b['time'],reason=reason,ambiguous=amb,pnl=pnl,modeled_cost=(spread+10)*position['lots'],segment='validation' if position['entered']>=split else 'exploratory'))
                position=None
                if negative>=20 or streak>=3:paused=True
        # Entry only at the next open; one-position/no reversal on an exit bar.
        for l in levels:
            if l['state']!='PENDING':continue
            l['state']='CONSUMED'
            if b['time']!=l['confirmation']+dt:skips['MISSED_ENTRY']+=1;continue
            if paused or was_position or position:skips['RISK_OR_POSITION']+=1;continue
            # Context available at entry open, not this bar's future close.
            h_open=[x for x in series[ctf] if x['closed'] and x['time']+INTERVAL[ctf]<=b['time']]
            if not trend(h_open,INTERVAL[ctf],l['side']=='resistance'):skips['ENTRY_CONTEXT_FAILED']+=1;continue
            p,reason=fill_plan(l,b,spread,equity)
            if reason:skips[reason]+=1;continue
            position=p
            # Entry is at bar open, so its subsequent range can trigger an exit.
            fill,reason,amb=exit_fill(p,b,spread)
            if fill is not None:
                pnl=(fill-p['entry'])*(1 if p['long'] else -1)*p['lots'];equity+=pnl;peak=max(peak,equity);dd=max(dd,peak-equity);negative+=max(0,-pnl);streak=streak+1 if pnl<0 else 0
                trades.append(dict(p,exit=fill,exit_bar=b['time'],reason=reason,ambiguous=amb,pnl=pnl,modeled_cost=(spread+10)*p['lots'],segment='validation' if p['entered']>=split else 'exploratory'));position=None
                if negative>=20 or streak>=3:paused=True
            break
        for l in levels:
            if l['state'] not in ('ARMED','BREAKOUT','RETEST'):continue
            if now>=l['expires']:l['state']='EXPIRED';skips['LEVEL_EXPIRED']+=1;continue
            if paused:continue
            long=l['side']=='resistance';L=l['price'];d=L*.0005
            if l['state']=='ARMED':
                if not previous or b['time']<l['created']:continue
                crossing=b['close']>L+d and previous['close']<=L+d if long else b['close']<L-d and previous['close']>=L-d
                if not crossing:continue
                if not trend(h,INTERVAL[ctf],long):l['state']='CONTEXT_FAILED';skips['CONTEXT_FAILED']+=1;continue
                targets=[t for t in levels if t['id']!=l['id'] and t['side']==l['side'] and t['state']=='ARMED' and t['created']<now and now<t['expires'] and (t['price']>L+d if long else t['price']<L-d)]
                if not targets:l['state']='NO_TARGET';skips['NO_TARGET']+=1;continue
                l.update(state='BREAKOUT',target=min(targets,key=lambda t:abs(t['price']-L))['price'],post=[],breakout=b['time']);continue
            l['post'].append(b)
            invalid=b['low']<L-d or b['close']<L if long else b['high']>L+d or b['close']>L
            if invalid:l['state']='INVALIDATED';skips['INVALIDATED']+=1;continue
            if len(l['post'])>6:l['state']='EXPIRED';skips['RETEST_EXPIRED']+=1;continue
            if b['low']<=L+d and b['high']>=L-d:l['state']='RETEST'
            confirm=b['close']>L+d and b['close']>b['open'] if long else b['close']<L-d and b['close']<b['open']
            if l['state']=='RETEST' and confirm:
                if not trend(h,INTERVAL[ctf],long):l['state']='CONTEXT_FAILED';skips['CONFIRM_CONTEXT_FAILED']+=1;continue
                l.update(state='PENDING',confirmation=b['time'],extreme=min(x['low'] for x in l['post']) if long else max(x['high'] for x in l['post']))
        # Discover levels only after this bar is processed, never retroactively.
        lb=[x for x in series[ltf] if x['closed'] and x['time']+INTERVAL[ltf]<=now]
        if lb and lb[-1]['time']!=lastmap:
            add_levels(lb,now,levels,used);lastmap=lb[-1]['time']
        previous=b
    segments={}
    for segment in ['exploratory','validation']:
        ts=[t for t in trades if t['segment']==segment];segments[segment]={'closed_trades':len(ts),'net_pnl':round(sum(t['pnl'] for t in ts),4),'win_rate':sum(t['pnl']>0 for t in ts)/len(ts) if ts else None}
    return dict(status='UNPROVEN / MODELED / MARGIN UNVERIFIED',variant=variant,timeframes=dict(levels=ltf,entry=etf,context=ctf),period=dict(start=start,end=end,validation_start=split,bars=len(bars)),spread_assumption=spread,registered_levels=len(levels),skips=dict(skips),closed_trades=len(trades),net_pnl=round(equity-1000,4),modeled_costs=round(sum(t['modeled_cost'] for t in trades),4),realized_drawdown=round(dd,4),ambiguous=sum(t['ambiguous'] for t in trades),segments=segments,risk_paused=paused,gaps=gaps,uncertain_position=uncertain,open_position=position,trades=trades,levels=levels)
