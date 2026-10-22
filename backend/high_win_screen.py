"""Bounded fixed-rule screen, not an optimizer and never a live trading engine."""
import math
from bisect import bisect_right
from collections import Counter
from datetime import datetime,timezone,timedelta
from statistics import mean,pstdev
from .auto_research import exit_fill
from .engine import round_tick

FAMILIES=('BB_REENTRY','FAILED_RANGE_BREAK','EMA_TREND_RECLAIM')

def contiguous(bs,dt):
    return bool(bs) and all(b['time']-a['time']==dt for a,b in zip(bs,bs[1:]))

def ema(values,period):
    out=[];value=values[0]
    for x in values:value+=2/(period+1)*(x-value);out.append(value)
    return out

def atr(bs):
    return mean(max(b['high']-b['low'],abs(b['high']-a['close']),abs(b['low']-a['close'])) for a,b in zip(bs[-15:],bs[-14:]))

def signal(family,prior,b,m5):
    if len(prior)<21 or len(m5)<40 or not contiguous(prior[-21:]+[b],60) or not contiguous(m5,300):return None
    ps=prior[-20:];values=[x['close'] for x in prior];a=atr(prior)
    if a<=0:return None
    closes=[x['close'] for x in m5];e5=ema(closes,20);a5=atr(m5)
    flat=abs(e5[-1]-e5[-6])<=.25*a5
    bullish=b['close']>b['open'];bearish=b['close']<b['open'];long=None;target=None
    if family=='BB_REENTRY':
        if not flat:return None
        mid=mean(x['close'] for x in ps);sd=pstdev(x['close'] for x in ps)
        if sd<=0:return None
        lo=mid-2*sd;hi=mid+2*sd
        if prior[-1]['close']<=lo and b['close']>lo and bullish:long=True
        elif prior[-1]['close']>=hi and b['close']<hi and bearish:long=False
        target=mid
    elif family=='FAILED_RANGE_BREAK':
        if not flat:return None
        low=min(x['low'] for x in ps);high=max(x['high'] for x in ps)
        if b['low']<low and b['close']>low and bullish:long=True
        elif b['high']>high and b['close']<high and bearish:long=False
        target=(high+low)/2
    elif family=='EMA_TREND_RECLAIM':
        e9=ema(values,9)[-1];e21=ema(values,21)[-1]
        if closes[-1]>e5[-1]>e5[-2] and e9>e21 and prior[-1]['close']<=e9 and b['low']<=e9 and b['close']>e9 and bullish:long=True
        elif closes[-1]<e5[-1]<e5[-2] and e9<e21 and prior[-1]['close']>=e9 and b['high']>=e9 and b['close']<e9 and bearish:long=False
        if long is not None:target=b['close']+(a if long else -a)
    else:raise ValueError('Unknown signal family')
    if long is None:return None
    stop=b['low']-.25*a if long else b['high']+.25*a
    return dict(long=long,stop=round_tick(stop,.01,up=not long),target=round_tick(target,.01,up=not long),signal=b['time'],context_last=m5[-1]['time'],atr=a)

def plan(s,b,spread,min_rr,equity,risk_fraction=.005,max_risk=5,target_net_r=None):
    if not (math.isfinite(risk_fraction) and 0<risk_fraction<=1 and math.isfinite(max_risk) and max_risk>0):raise ValueError("Invalid research risk settings")
    sign=1 if s['long'] else -1;entry=b['open']+(spread if s['long'] else 0)+sign*5
    loss=sign*(entry-s['stop'])+5;gain=sign*(s['target']-entry)-5
    if loss<=0 or gain<=0 or gain/loss<min_rr:return None,'COST_FAILED'
    original_target=s['target']
    if target_net_r is not None:
        if not math.isfinite(target_net_r) or target_net_r<min_rr:raise ValueError('Target cap below minimum net R')
        cap=round_tick(entry+sign*(target_net_r*loss+5),.01,up=s['long'])
        target=min(original_target,cap) if s['long'] else max(original_target,cap)
        s=dict(s,target=target,original_target=original_target,target_cap_net_r=target_net_r)
        gain=sign*(target-entry)-5
    lots=math.floor(min(max_risk,risk_fraction*equity)/loss/.01+1e-9)*.01
    if lots<.01 or lots>200:return None,'SIZE_FAILED'
    return dict(s,entry=entry,entered=b['time'],deadline=b['time']+1800,lots=round(lots,2),net_rr=gain/loss,planned_risk=loss*round(lots,2),risk_budget=min(max_risk,risk_fraction*equity)),None

def reverse_signal(s,spread):
    """Swap direction/exits while preserving underlying bid trigger boundaries."""
    shift=spread if s['long'] else -spread
    return dict(s,long=not s['long'],stop=round_tick(s['target']+shift,.01,up=s['long']),target=round_tick(s['stop']+shift,.01,up=s['long']),original_long=s['long'],original_stop=s['stop'],original_target=s['target'],reversed_entry=True)


def news_blocked(stamp,windows):
    return any(w['start']<=stamp<w['end'] for w in (windows or []))


def wilson(w,n):
    if not n:return None
    z=1.959963984540054;p=w/n;den=1+z*z/n
    center=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [max(0,center-half),min(1,center+half)]

def metrics(trades):
    wins=[t['pnl'] for t in trades if t['pnl']>0];losses=[t['pnl'] for t in trades if t['pnl']<0];n=len(trades)
    return dict(closed_trades=n,wins=len(wins),losses=len(losses),breakeven=n-len(wins)-len(losses),win_rate=len(wins)/n if n else None,win_rate_wilson95=wilson(len(wins),n),net_pnl=round(sum(t['pnl'] for t in trades),4),average_win=mean(wins) if wins else None,average_loss=mean(losses) if losses else None,profit_factor=sum(wins)/-sum(losses) if losses else None,modeled_costs=round(sum(t['modeled_cost'] for t in trades),4))

def manila_day(stamp):
    return datetime.fromtimestamp(stamp,timezone(timedelta(hours=8))).date().isoformat()


def volume_confirmation(prior,b,multiplier=1.5):
    """Completed signal candle vs 20 preceding M1 bars; no future data."""
    window=prior[-20:]
    if len(window)!=20 or not contiguous(window+[b],60):return False,None
    values=[x.get('tick_volume') for x in window+[b]]
    if any(type(v) is not int or v<0 for v in values):return False,None
    average=mean(values[:-1])
    if average<=0:return False,None
    ratio=values[-1]/average
    return ratio>multiplier,ratio


def run(data,family,spread,min_rr,start,end,risk_fraction=.005,max_risk=5,target_net_r=None,reverse_entries=False,news_windows=None,signal_cache=None,daily_reset=False,cooldown_seconds=0,max_daily_entries=None,drawdown_limit=None,volume_multiplier=None):
    if volume_multiplier is not None and (not math.isfinite(volume_multiplier) or volume_multiplier<=0):raise ValueError('Invalid volume multiplier')
    if volume_multiplier is not None:
        required=[b for b in data['candles']['M1'] if b['closed'] and start-20*60<=b['time']<end]
        if not required or any(type(b.get('tick_volume')) is not int or b['tick_volume']<0 for b in required) or not any(b['tick_volume']>0 for b in required):
            return dict(status='BLOCKED',reason='Missing or invalid historical tick volume',family=family)
    entries=[b for b in data['candles']['M1'] if b['closed']];context=[b for b in data['candles']['M5'] if b['closed']];ct=[b['time']+300 for b in context]
    if not entries or entries[0]['time']>start-21*60 or entries[-1]['time']+60<end or not context or context[0]['time']>start-60*300:return dict(status='BLOCKED',reason='Insufficient history',family=family)
    trades=[];position=None;pending=None;previous=None;skips=Counter();equity=1000.;peak=1000.;dd=0.;negative=0.;streak=0;paused=False;paused_at=None;gaps=[];uncertain=None;signals=0;processed_end=start
    day=None;entries_today=0;daily={};permanent_pause=False;cooldown_until=0;pause_events=[]
    def close(p,fill,reason,amb,b):
        nonlocal equity,peak,dd,negative,streak,paused,paused_at,permanent_pause,cooldown_until
        pnl=(fill-p['entry'])*(1 if p['long'] else -1)*p['lots'];equity+=pnl;peak=max(peak,equity);dd=max(dd,peak-equity);negative+=max(0,-pnl);streak=streak+1 if pnl<0 else 0
        trades.append(dict(p,exit=fill,exit_bar=b['time'],pnl=pnl,reason=reason,ambiguous=amb,modeled_cost=(spread+10)*p['lots']))
        if cooldown_seconds:cooldown_until=b['time']+60+cooldown_seconds
        if daily_reset:
            d=daily[day];d['closed_trades']+=1;d['pnl']+=pnl;d['negative_closes']+=max(0,-pnl)
        if negative>=20 or streak>=3:
            if not paused:pause_events.append(dict(time=b['time'],kind='DAY_LOSS_PAUSE' if daily_reset else 'RUN_LOSS_PAUSE',day=day))
            paused=True;paused_at=b['time']
            if daily_reset:daily[day]['loss_paused']=True
        if drawdown_limit is not None and peak-equity>=drawdown_limit:
            if not permanent_pause:pause_events.append(dict(time=b['time'],kind='ACCOUNT_DRAWDOWN_STOP',day=day))
            permanent_pause=True;paused=True;paused_at=b['time']
    for i,b in enumerate(entries):
        if b['time']<start:continue
        if b['time']+60>end:break
        processed_end=b['time']+60
        current_day=manila_day(b['time'])
        if current_day!=day:
            day=current_day;entries_today=0
            if daily_reset:
                negative=0.;streak=0;paused=permanent_pause
                if not permanent_pause:paused_at=None
                daily[day]=dict(entries=0,closed_trades=0,pnl=0.,negative_closes=0.,loss_paused=False)
        if previous and b['time']!=previous['time']+60:
            gaps.append(dict(after=previous['time'],before=b['time']))
            if pending:skips['PENDING_DATA_GAP']+=1;pending=None
            if position:uncertain=dict(position,gap=gaps[-1]);position=None;break
        had_position=position is not None
        if position:
            if b['time']>=position['deadline']:fill=b['open']+(0 if position['long'] else spread)+(-5 if position['long'] else 5);reason='TIME';amb=False
            else:fill,reason,amb=exit_fill(position,b,spread)
            if fill is not None:close(position,fill,reason,amb,b);position=None
        if pending:
            s=pending;pending=None
            if b['time']!=s['signal']+60:skips['MISSED_ENTRY']+=1
            elif had_position or position or paused:skips['RISK_OR_POSITION']+=1
            elif max_daily_entries is not None and entries_today>=max_daily_entries:skips['DAY_ENTRY_LIMIT']+=1
            elif b['time']<cooldown_until:skips['EXIT_COOLDOWN']+=1
            elif news_blocked(b['time'],news_windows):skips['NEWS_ENTRY_BLOCKED']+=1
            else:
                if reverse_entries:s=reverse_signal(s,spread)
                p,reason=plan(s,b,spread,min_rr,equity,risk_fraction,max_risk,target_net_r)
                if reason:skips[reason]+=1
                else:
                    position=p;entries_today+=1
                    if daily_reset:daily[day]['entries']+=1
                    fill,reason,amb=exit_fill(p,b,spread)
                    if fill is not None:close(p,fill,reason,amb,b);position=None
        # No entry/exit reversal on one candle. Signals during a pause remain diagnostics only.
        key=(family,b['time'])
        if signal_cache is not None and key in signal_cache:s=signal_cache[key]
        else:
            j=bisect_right(ct,b['time']);m5=context[max(0,j-60):j]
            s=signal(family,entries[max(0,i-60):i],b,m5)
            if signal_cache is not None:signal_cache[key]=s
        if s:
            signals+=1
            in_news=news_blocked(b['time']+60,news_windows)
            if in_news:skips['RAW_SIGNAL_IN_NEWS_WINDOW']+=1
            if paused:
                skips['SIGNAL_DURING_RISK_PAUSE']+=1
                if in_news:skips['NEWS_SIGNAL_ALREADY_RISK_PAUSED']+=1
            elif position or had_position:
                skips['SIGNAL_WHILE_POSITION']+=1
                if in_news:skips['NEWS_SIGNAL_ALREADY_POSITION_BLOCKED']+=1
            elif max_daily_entries is not None and entries_today>=max_daily_entries:skips['DAY_ENTRY_LIMIT']+=1
            elif b['time']+60<cooldown_until:skips['EXIT_COOLDOWN']+=1
            elif in_news:skips['NEWS_SIGNAL_BLOCKED']+=1
            else:
                if volume_multiplier is not None:
                    allowed,ratio=volume_confirmation(entries[max(0,i-20):i],b,volume_multiplier)
                    if not allowed:
                        skips['VOLUME_FAILED' if ratio is not None else 'VOLUME_UNAVAILABLE']+=1
                        previous=b
                        continue
                    s=dict(s,tick_volume=b['tick_volume'],relative_tick_volume=ratio)
                pending=s
        previous=b
    result=metrics(trades)
    result.update(status='UNPROVEN / CANDLE MODELED / MARGIN UNVERIFIED',family=family,spread=spread,min_net_rr=min_rr,risk_fraction=risk_fraction,max_risk=max_risk,target_net_r=target_net_r,reverse_entries=reverse_entries,news_windows=news_windows,start=start,end=end,processed_end=processed_end,signals=signals,skips=dict(skips),realized_drawdown=round(dd,4),risk_paused=paused,paused_at=paused_at,gaps=gaps,uncertain_position=uncertain,open_position=position,pending_signal=pending,ambiguous=sum(t['ambiguous'] for t in trades),trades=trades)
    result.update(daily_reset=daily_reset,cooldown_seconds=cooldown_seconds,max_daily_entries=max_daily_entries,drawdown_limit=drawdown_limit,permanent_pause=permanent_pause,pause_events=pause_events,daily=daily,initial_balance=1000,volume_multiplier=volume_multiplier)
    result['research_flag']=result['closed_trades']>=100 and result['win_rate']>=.8 and result['net_pnl']>0 and not position and not uncertain
    return result
