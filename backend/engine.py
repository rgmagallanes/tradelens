"""Approved v1 paper-only reducer. No MT5 order API. Persisted decisions use broker evidence."""
import hashlib,json,math,time,uuid
from datetime import datetime,timezone,timedelta
from decimal import Decimal,ROUND_FLOOR,ROUND_CEILING
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'strategy/frozen/parameters-v1.json').read_text())
MANIFEST=json.loads((ROOT/'strategy/frozen/manifest-v1.json').read_text())
VERSION=P['version']
ACTIVE={'ARMED','BREAKOUT_CONFIRMED','RETEST_SEEN','ENTRY_ELIGIBLE'}
def integrity():
    return all(hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==MANIFEST[key] for path,key in [('strategy/frozen/parameters-v1.json','parameters_sha256'),('strategy/frozen/breakout-retest-v1.md','spec_sha256')])
def day(now): return datetime.fromtimestamp(now,timezone(timedelta(hours=8))).date().isoformat()
def initial():
    return dict(enabled=False,news_pause=False,levels=[],position=None,closed=[],last_bar=None,last_poll=None,last_quote=None,recovery=0,recovering=True,events=[],config={},pause_date=None,needs_resume=False,reason='Configure and verify paper prerequisites before starting.')
def event(s,kind,now,**data): s['events'].append(dict(kind=kind,received_utc=now,version=VERSION,**data))
def finish(s,l,state,now,**data):
    l['state']=state;event(s,state,now,level_id=l['id'],**data)
def round_tick(value,tick,up=False):
    d=Decimal(str(value))/Decimal(str(tick));return float(d.to_integral_value(rounding=ROUND_CEILING if up else ROUND_FLOOR)*Decimal(str(tick)))
def evidence(bars,L,side):
    """Eligible touch timestamps whose full reaction is already known."""
    bars=[b for b in bars if b['closed']][-96:];delta=L*P['tolerance_fraction'];found=[]
    for i,b in enumerate(bars):
        touched=b['low']<=L+delta and b['high']>=L-delta
        close_ok=b['close']<=L if side=='resistance' else b['close']>=L
        reaction=[r for r in bars[i+1:i+4] if (r['close']<=L-2*delta if side=='resistance' else r['close']>=L+2*delta)]
        if touched and close_ok and reaction: found.append(dict(time=b['time'],index=i,bar=b,reaction=reaction[0]))
    return found

def register(s,L,side,touches,bars,now,context):
    if not math.isfinite(L) or L<=0 or side not in ('support','resistance'): raise ValueError('Invalid level')
    eligible={e['time']:e for e in evidence(bars,L,side)}
    if len(set(touches))<2 or any(t not in eligible for t in touches): raise ValueError('Choose at least two eligible M15 reaction bars.')
    selected=sorted((eligible[t] for t in set(touches)),key=lambda e:e['index'])
    if any(b['index']-a['index']<3 for a,b in zip(selected,selected[1:])): raise ValueError('Touch bars must be separated by at least three M15 openings.')
    l=dict(id=str(uuid.uuid4()),price=L,side=side,created=now,expires=now+P['level_lifetime_seconds'],state='ARMED',context_reviewed=context,evidence=selected)
    s['levels'].append(l);event(s,'LEVEL_REGISTERED',now,level=l);return l

def prerequisites(config,q):
    missing=[]
    if not integrity(): missing.append('Frozen strategy integrity check failed')
    if not config.get('parity_verified'): missing.append('Independent MT5 candle comparison not confirmed')
    if not config.get('verification_note','').strip(): missing.append('Verification reference is required')
    if not config.get('commission_confirmed') or config.get('commission_per_lot_side') is None: missing.append('Commission not confirmed (unknown is not zero)')
    if not config.get('commission_source','').strip(): missing.append('Commission source/date is required')
    if q.get('chart_basis')!='bid': missing.append('Broker candle price basis not verified as bid')
    if q.get('currency')!='USD': missing.append('USD demo account required for this paper model')
    for k in ('tick_size','contract_size','volume_min','volume_step','volume_max','margin_buy_per_lot','margin_sell_per_lot'):
        if type(q.get(k)) not in (float,int) or not math.isfinite(q[k]) or q[k]<=0: missing.append('Missing broker specification: '+k)
    return missing

def risk_gate(s,now):
    if s.get('needs_resume'): return 'Risk pause requires explicit resume on a later Manila date'
    losses=sum(-p['pnl'] for p in s['closed'] if p['pnl']<0 and day(p['closed_at'])==day(now))
    streak=0
    for p in reversed(s['closed']):
        if p['pnl']>=0 or p['closed_at']<s.get('resume_after',0): break
        streak+=1
    if losses>=P['daily_negative_loss_limit'] or streak>=P['consecutive_loss_limit']:
        s.update(pause_date=day(now),needs_resume=True);event(s,'RISK_PAUSE',now,negative_losses=losses,losing_streak=streak)
        return 'Daily loss or consecutive-loss limit reached'
    return None

def context(h1,long):
    bars=[b for b in h1 if b['closed']]
    if len(bars)<2:return False
    a,b=bars[-2:]
    if b['time']-a['time']!=3600:return False
    return b['close']>a['high'] if long else b['close']<a['low']

def sized_plan(s,l,q,now):
    long=l['side']=='resistance';sign=1 if long else -1;slip=P['slippage_usd_per_btc_per_fill'];tick=q['tick_size'];contract=q['contract_size']
    entry=q['ask']+slip if long else q['bid']-slip
    stop=round_tick(l['extreme']-l['price']*P['stop_buffer_fraction'] if long else l['extreme']+l['price']*P['stop_buffer_fraction'],tick,up=not long)
    targets=[t for t in s['levels'] if t['id']!=l['id'] and t['side']==l['side'] and t['created']<=l['breakout_received'] and t.get('registered_broker_tick',0)<(l['breakout_bar']['time']+300)*1000 and now<t['expires'] and t['state']=='ARMED' and (t['price']>entry if long else t['price']<entry)]
    if not targets:return None,'NO_TARGET'
    target_level=min(targets,key=lambda t:abs(t['price']-entry));target=round_tick(target_level['price'],tick,up=not long)
    fee=s['config']['commission_per_lot_side'];loss=((entry-stop)*sign+slip)*contract+2*fee;gain=((target-entry)*sign-slip)*contract-2*fee
    if loss<=0 or gain/loss<P['min_net_rr']:return None,'COST_FAILED'
    equity=P['initial_equity']+sum(p['pnl'] for p in s['closed']);budget=min(P['max_risk_usd'],equity*P['risk_fraction'])
    lots=round_tick(min(budget/loss,q['volume_max']),q['volume_step'])
    margin=q['margin_buy_per_lot' if long else 'margin_sell_per_lot']*lots
    if lots<q['volume_min'] or lots<=0 or margin>equity:return None,'SIZE_FAILED'
    trade_id=hashlib.sha256(f"{VERSION}:{l['id']}:{l['breakout_bar']['time']}".encode()).hexdigest()[:32]
    return dict(id=trade_id,level_id=l['id'],target_level_id=target_level['id'],side='buy' if long else 'sell',entry=entry,stop=stop,target=target,lots=lots,contract=contract,commission_per_side=fee,slippage=slip,opened_at=now,deadline=now+P['max_hold_seconds'],risk_budget=budget,modeled_loss=loss*lots,modeled_gain=gain*lots,rr=gain/loss,margin=margin,entry_quote=dict(q),spec_hash=MANIFEST['spec_sha256'],parameters_hash=MANIFEST['parameters_sha256'],config=dict(s['config']),evidence=dict(l),quality='POLLING-BASED / NOT TICK-COMPLETE',uncertainty=False),None

def exits(s,q,now,monotonic_now=None,run_id=None):
    p=s['position']
    if not p:return False
    long=p['side']=='buy';side=q['bid'] if long else q['ask'];sign=1 if long else -1;reason=None
    if (side<=p['stop'] if long else side>=p['stop']): reason='STOP';fill=min(side,p['stop']) if long else max(side,p['stop'])
    elif (side>=p['target'] if long else side<=p['target']): reason='TARGET';fill=p['target']
    elif (monotonic_now>=p['deadline_monotonic'] if monotonic_now is not None and p.get('clock_run_id')==run_id else now>=p['deadline']):reason='TIME';fill=side
    if not reason:return False
    fill-=sign*p['slippage'];pnl=(fill-p['entry'])*sign*p['contract']*p['lots']-2*p['commission_per_side']*p['lots']
    p.update(status='CLOSED',closed_at=now,exit=fill,exit_quote=dict(q),exit_reason=reason,pnl=round(pnl,8))
    s['closed'].append(p);s['position']=None;event(s,'CLOSED',now,trade=p);risk_gate(s,now);return True

def candle_replay_exit(bar,stop,target,long):
    """Conservative ambiguous candle replay diagnostic; not tick-complete."""
    hit_stop=bar['low']<=stop if long else bar['high']>=stop
    hit_target=bar['high']>=target if long else bar['low']<=target
    return {'reason':'STOP' if hit_stop else 'TARGET' if hit_target else None,'ambiguous':hit_stop and hit_target}

def step(s,data,q,now,ready=True,monotonic_now=None,run_id=None):
    """Single observed snapshot; caller serializes and persists atomically."""
    bars=[b for b in data.get('M5',[]) if b['closed']];h1=data.get('H1',[])
    previous_poll=s.get('last_poll');was_gap=previous_poll is not None and (now-previous_poll>=P['freshness_seconds'] or now<previous_poll);s['last_poll']=now
    if not ready or was_gap:
        for l in s['levels']:
            if l['state'] in ACTIVE:finish(s,l,'STALE_FEED',now)
        if s['position'] and not s['position']['uncertainty']:
            s['position']['uncertainty']=True;event(s,'EXECUTION_UNCERTAINTY',now,trade_id=s['position']['id'])
        s.update(recovering=True,recovery=0,last_bar=bars[-1]['time'] if bars else None)
        s['reason']='Feed gap: waiting for two new contiguous completed M5 bars';return
    # Never execute exits twice or reverse on the closing snapshot.
    quote_id=q.get('tick_time_msc')
    if quote_id!=s.get('last_quote'):
        s['last_quote']=quote_id
        if exits(s,q,now,monotonic_now,run_id):return
    if not s['enabled']:
        s['last_bar']=bars[-1]['time'] if bars else None;return
    missing=prerequisites(s['config'],q)
    if missing:s['reason']='; '.join(missing);return
    if not bars:s['reason']='No completed M5 bars';return
    if s['last_bar'] is None:s['last_bar']=bars[-1]['time'];return
    new=[b for b in bars if b['time']>s['last_bar']]
    if len(new)>1 or (new and new[0]['time']!=s['last_bar']+300):
        for l in s['levels']:
            if l['state'] in ACTIVE:finish(s,l,'DATA_GAP',now)
        s.update(recovering=True,recovery=0,last_bar=bars[-1]['time'],reason='Missing M5 bars; recovering');return
    if s.get('recovering'):
        if new:s['recovery']+=1;s['last_bar']=new[0]['time']
        if s['recovery']>=P['recovery_bars']:s['recovering']=False
        s['reason']='Recovering feed' if s['recovering'] else 'Watching newly registered levels';return
    gate=risk_gate(s,now)
    if gate:s['reason']=gate;return
    if s['news_pause']:s['reason']='Manual news pause';return
    s['reason']='Watching closed M5 candles'
    for l in s['levels']:
        if l['state'] not in ACTIVE:continue
        if now>=l['expires']:finish(s,l,'EXPIRED',now);continue
        long=l['side']=='resistance';L=l['price'];d=L*P['tolerance_fraction']
        if l['state']=='ENTRY_ELIGIBLE':
            # Require a subsequent fresh quote; never reuse the confirmation snapshot.
            if now-l['detected_at']>P['entry_detection_seconds'] or q['tick_time_msc']/1000-l['confirmation_bar']['time']-300>P['entry_close_seconds']:
                finish(s,l,'MISSED_ENTRY',now);continue
            if q['tick_time_msc']<=l['confirmation_quote']:continue
            if s['position']:finish(s,l,'USER_CANCELLED',now,reason='Another paper position is open');continue
            if not context(h1,long):finish(s,l,'CONTEXT_FAILED',now);continue
            plan,reason=sized_plan(s,l,q,now)
            if reason:finish(s,l,reason,now);continue
            plan['h1_at_entry']=[p for p in h1 if p['closed']][-2:]
            plan['equity_at_entry']=P['initial_equity']+sum(p['pnl'] for p in s['closed'])
            if monotonic_now is not None:plan.update(deadline_monotonic=monotonic_now+P['max_hold_seconds'],clock_run_id=run_id)
            s['position']=plan;finish(s,l,'OPEN',now,trade_id=plan['id']);event(s,'OPEN',now,trade=plan);continue
        if not new:continue
        b=new[0];previous=next((p for p in bars if p['time']==b['time']-300),None)
        if l['state']=='ARMED':
            if not previous or not l['context_reviewed'] or b['time']<=l.get('registration_last_closed',0):continue
            # Strictly after registration; do not act on a preloaded breakout.
            if now<=l['created']:continue
            breakout=b['close']>L+d and previous['close']<=L+d if long else b['close']<L-d and previous['close']>=L-d
            if not breakout:continue
            if not context(h1,long):finish(s,l,'CONTEXT_FAILED',now);continue
            l.update(breakout_bar=b,breakout_received=now,h1_at_breakout=[p for p in h1 if p['closed']][-2:],count=0,post_bars=[],state='BREAKOUT_CONFIRMED');event(s,'BREAKOUT_CONFIRMED',now,level_id=l['id'],bar=b);continue
        l['count']+=1;l['post_bars'].append(b)
        if l['count']>P['retest_bars']:finish(s,l,'EXPIRED',now);continue
        invalid=(b['low']<L-d or b['close']<L) if long else (b['high']>L+d or b['close']>L)
        if invalid:finish(s,l,'INVALIDATED',now,bar=b);continue
        touched=b['low']<=L+d and b['high']>=L-d
        if touched and l['state']=='BREAKOUT_CONFIRMED':l['state']='RETEST_SEEN';event(s,'RETEST_SEEN',now,level_id=l['id'],bar=b)
        confirm=(b['close']>L+d and b['close']>b['open']) if long else (b['close']<L-d and b['close']<b['open'])
        if l['state']=='RETEST_SEEN' and confirm:
            l.update(state='ENTRY_ELIGIBLE',detected_at=now,confirmation_bar=b,confirmation_quote=q['tick_time_msc'],extreme=min(p['low'] for p in l['post_bars']) if long else max(p['high'] for p in l['post_bars']))
            event(s,'ENTRY_ELIGIBLE',now,level_id=l['id'],bar=b)
    if new:s['last_bar']=new[0]['time']
