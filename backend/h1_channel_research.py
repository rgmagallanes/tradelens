"""Fixed H1 channel trend experiment, independent from live paper state."""
import math
from collections import Counter
from .engine import round_tick


def contiguous(bs):return len(bs)>0 and all(b['time']-a['time']==3600 for a,b in zip(bs,bs[1:]))

def atr_series(bars):
    out={};trs=[];atr=None;previous=None
    for b in bars:
        if previous is None or b['time']-previous['time']!=3600:trs=[];atr=None
        else:
            tr=max(b['high']-b['low'],abs(b['high']-previous['close']),abs(b['low']-previous['close']))
            if atr is None:
                trs.append(tr)
                if len(trs)==14:atr=sum(trs)/14
            else:atr=(13*atr+tr)/14
        out[b['time']]=atr;previous=b
    return out

def breakout(prior,b):
    prior=prior[-20:]
    if len(prior)<20 or not contiguous(prior+[b]):return None
    if b['close']>max(x['high'] for x in prior):return True
    if b['close']<min(x['low'] for x in prior):return False
    return None

def channel_exit(prior,b,long):
    prior=prior[-10:]
    if len(prior)<10 or not contiguous(prior+[b]):return False
    return b['close']<min(x['low'] for x in prior) if long else b['close']>max(x['high'] for x in prior)

def trend_allowed(completed,long):
    bs=completed[-100:]
    if len(bs)<55 or not contiguous(bs):return False
    value=sum(b['close'] for b in bs[:50])/50;values=[value]
    for b in bs[50:]:
        value+=(2/51)*(b['close']-value);values.append(value)
    return bs[-1]['close']>values[-1] and values[-1]>values[-6] if long else bs[-1]['close']<values[-1] and values[-1]<values[-6]

def range_allowed(b,prior_atr):
    return prior_atr is not None and prior_atr>0 and b['high']-b['low']<=2*prior_atr


def enter(s,b,spread,equity):
    long=s['long'];sign=1 if long else -1;entry=b['open']+(spread if long else 0)+sign*5
    stop=round_tick(entry-sign*2*s['atr'],.01,up=not long)
    unit_loss=sign*(entry-stop)+5;budget=.005*equity
    if unit_loss<=0:return None,'INVALID_RISK'
    lots=math.floor(budget/unit_loss/.01+1e-9)*.01
    if lots<.01 or lots>200:return None,'SIZE_FAILED'
    return dict(long=long,entry=entry,stop=stop,lots=round(lots,2),entered=b['time'],signal=s['signal'],atr=s['atr'],risk_budget=budget,planned_loss=unit_loss*round(lots,2),notional=entry*round(lots,2)),None

def stop_fill(p,b,spread,opening_only=False):
    long=p['long'];adjust=0 if long else spread;op=b['open']+adjust
    hit=(op<=p['stop'] if long else op>=p['stop']) if opening_only else (b['low']+adjust<=p['stop'] if long else b['high']+adjust>=p['stop'])
    if not hit:return None
    return (min(op,p['stop']) if long else max(op,p['stop']))+(-5 if long else 5)

def run(data,start,end,spread=6.4,initial=1000,profile="baseline"):
    if profile not in ("baseline","ema50","ema50_range"):raise ValueError("Unknown fixed H1 profile")
    bars=[b for b in data['candles']['H1'] if b['closed']]
    if not bars or bars[0]['time']>start-21*3600 or bars[-1]['time']+3600<end:return dict(status='BLOCKED',reason='Incomplete H1 window or warmup')
    atrs=atr_series(bars);position=None;pending=None;scheduled_exit=None;trades=[];equity=initial;peak=initial;dd=0.;negative=0.;streak=0;paused=False;paused_at=None;skips=Counter();gaps=[];uncertain=None;raw_signals=0;processed=start;last=None;size_rejections=[];active_bars=0;risk_paused_bars=0
    def close(p,fill,reason,b,exit_signal=None):
        nonlocal equity,peak,dd,negative,streak,paused,paused_at
        pnl=(fill-p['entry'])*(1 if p['long'] else -1)*p['lots'];equity+=pnl;peak=max(peak,equity);dd=max(dd,peak-equity);negative+=max(0,-pnl);streak=streak+1 if pnl<0 else 0
        trades.append(dict(p,exit=fill,exit_bar=b['time'],exit_signal=exit_signal,reason=reason,pnl_excluding_swaps=pnl,modeled_cost=(spread+10)*p['lots'],hold_hours=(b['time']-p['entered'])/3600))
        if negative>=.02*initial or streak>=3:paused=True;paused_at=b['time']
    for i,b in enumerate(bars):
        if b['time']<start:continue
        if b['time']+3600>end:break
        processed=b['time']+3600
        if paused:risk_paused_bars+=1
        else:active_bars+=1
        if last is not None and b['time']!=last+3600:
            gaps.append(dict(after=last,before=b['time']));pending=None;scheduled_exit=None
            if position:uncertain=dict(position,gap=gaps[-1]);position=None;break
        occupied_open=position is not None
        if position and scheduled_exit is not None:
            fill=stop_fill(position,b,spread,opening_only=True)
            reason='STOP_GAP' if fill is not None else 'CHANNEL_EXIT'
            if fill is None:fill=b['open']+(0 if position['long'] else spread)+(-5 if position['long'] else 5)
            close(position,fill,reason,b,scheduled_exit);position=None;scheduled_exit=None
        if pending:
            s=pending;pending=None
            if b['time']!=s['signal']+3600:skips['MISSED_ENTRY']+=1
            elif occupied_open or position or paused:skips['RISK_OR_POSITION']+=1
            elif profile!='baseline' and not trend_allowed(bars[:i],s['long']):skips['ENTRY_TREND_FILTER']+=1
            else:
                p,reason=enter(s,b,spread,equity)
                if reason:
                    skips[reason]+=1
                    if reason=='SIZE_FAILED':
                        sign=1 if s['long'] else -1;ep=b['open']+(spread if s['long'] else 0)+sign*5
                        stop=round_tick(ep-sign*2*s['atr'],.01,up=not s['long'])
                        size_rejections.append(dict(signal=s['signal'],entry_time=b['time'],equity=equity,minimum_equity_for_min_lot=(sign*(ep-stop)+5)*.01/.005))
                else:position=p
        if position:
            fill=stop_fill(position,b,spread)
            if fill is not None:close(position,fill,'STOP',b);position=None
        if position and channel_exit(bars[:i],b,position['long']):scheduled_exit=b['time']
        direction=breakout(bars[:i],b)
        if direction is not None:
            raw_signals+=1
            if paused:skips['SIGNAL_DURING_RISK_PAUSE']+=1
            elif position or occupied_open:skips['SIGNAL_WHILE_POSITION']+=1
            elif atrs[b['time']] is None or atrs[b['time']]<=0:skips['ATR_UNAVAILABLE']+=1
            elif profile!='baseline' and not trend_allowed(bars[:i+1],direction):skips['SIGNAL_TREND_FILTER']+=1
            elif profile=='ema50_range' and not range_allowed(b,atrs.get(b['time']-3600)):skips['EXPANSION_FILTER']+=1
            else:pending=dict(long=direction,signal=b['time'],atr=atrs[b['time']])
        last=b['time']
    wins=[t['pnl_excluding_swaps'] for t in trades if t['pnl_excluding_swaps']>0];losses=[t['pnl_excluding_swaps'] for t in trades if t['pnl_excluding_swaps']<0]
    mark=None
    if position and processed==end:
        final=next(b for b in bars if b['time']+3600==end);fill=final['close']+(0 if position['long'] else spread)+(-5 if position['long'] else 5)
        mark=dict(mark_bid=final['close'],illustrative_exit_fill=fill,unrealized_excluding_swaps=(fill-position['entry'])*(1 if position['long'] else -1)*position['lots'],not_closed=True)
    costs=sum(t['modeled_cost'] for t in trades)
    return dict(status='UNPROVEN / MODELED / SWAPS AND MARGIN UNVERIFIED',initial_balance=initial,spread=spread,profile=profile,active_bars=active_bars,risk_paused_bars=risk_paused_bars,size_rejections=size_rejections,start=start,end=end,processed_end=processed,evaluation_bars=sum(start<=b['time'] and b['time']+3600<=end for b in bars),raw_signals=raw_signals,skips=dict(skips),closed_trades=len(trades),wins=len(wins),losses=len(losses),win_rate=len(wins)/len(trades) if trades else None,pnl_excluding_swaps=round(equity-initial,4),modeled_costs=round(costs,4),realized_drawdown=round(dd,4),profit_factor=sum(wins)/-sum(losses) if losses else None,average_win=sum(wins)/len(wins) if wins else None,average_loss=sum(losses)/len(losses) if losses else None,risk_paused=paused,paused_at=paused_at,gaps=gaps,uncertain_position=uncertain,open_position=position,open_position_mark=mark,pending_signal=pending,max_notional=max([t['notional'] for t in trades]+([position['notional']] if position else [])+[0]),trades=trades)
