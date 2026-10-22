import json, math, sqlite3, time, os
from pathlib import Path
import asyncio
from contextlib import asynccontextmanager
from .paper_service import PaperService
from . import engine, mt5_journal
from typing import Literal, Optional
from .history import read_history, archive, INTERVALS
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DB = Path(__file__).with_name('studio.sqlite3')
def paper(): return PaperService(DB,BRIDGE_PATH,bridge_status)

@asynccontextmanager
async def lifespan(app):
    paper().restart()
    async def worker():
        while True:
            try: await asyncio.to_thread(paper().poll)
            except Exception as exc:
                # Keep service available; failures cannot enable trading.
                app.state.paper_error=type(exc).__name__
            try: await asyncio.to_thread(mt5_journal.sync,DB,BRIDGE_PATH.with_name('studio-trades.json'))
            except Exception as exc: app.state.journal_error=type(exc).__name__
            await asyncio.sleep(2)
    task=asyncio.create_task(worker())
    yield
    task.cancel()
    try: await task
    except asyncio.CancelledError: pass

app = FastAPI(title='BTC Studio — paper trading only',lifespan=lifespan)
def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
    c.execute('CREATE TABLE IF NOT EXISTS records(id INTEGER PRIMARY KEY, created REAL, kind TEXT, payload TEXT)')
    return c

def record(kind,payload):
    with db() as c:
        cur=c.execute('INSERT INTO records(created,kind,payload) VALUES(?,?,?)',(time.time(),kind,json.dumps(payload)))
        return cur.lastrowid

def candles(tf='M5',step=0):
    interval={'M5':300,'M15':900,'H1':3600,'H4':14400}[tf]
    start=1760313600
    result=[]
    for i in range(150+step):
        o=70000+9*i+230*math.sin(i/9)+110*math.sin(i/3)
        close=70000+9*(i+1)+230*math.sin((i+1)/9)+110*math.sin((i+1)/3)
        result.append(dict(time=start+i*interval,open=round(o,2),high=round(max(o,close)+40+20*abs(math.sin(i)),2),low=round(min(o,close)-40-20*abs(math.cos(i)),2),close=round(close,2),tick_volume=round(300+180*abs(math.sin(i/4))+((i*37)%120))))
    return result

class Plan(BaseModel):
    side: Literal['buy','sell']='buy'
    entry: float=Field(gt=0,le=10000000)
    stop: float=Field(gt=0,le=10000000)
    target: float=Field(gt=0,le=10000000)
    risk: float=Field(gt=0,le=100)
    spread: float=Field(20,ge=0,le=10000)
    slippage: float=Field(5,ge=0,le=10000)

@app.post('/api/plan')
def plan(p:Plan):
    direction=1 if p.side=='buy' else -1
    distance=(p.entry-p.stop)*direction
    reward=(p.target-p.entry)*direction
    if distance<=0 or reward<=0: raise HTTPException(422,'Stop and target must be on the correct sides of entry.')
    # Illustrative 1 BTC/lot, 0.01 lot step; replaced only after verified broker specs.
    loss=distance+p.spread+2*p.slippage
    size=math.floor((p.risk/loss)*100+1e-9)/100
    net=reward-p.spread-2*p.slippage
    return dict(lots=size,estimated_loss=round(size*loss,2),estimated_gain=round(size*net,2),rr=round(net/loss,2),eligible=size>=.01 and net>0,assumptions='Illustrative: 1 BTC/lot, 0.01 lot step, zero commission; spread once, slippage on both fills.')

class Simulate(Plan):
    confirmed: bool=False
@app.post('/api/simulate')
def simulate(p:Simulate):
    if not p.confirmed: raise HTTPException(422,'Complete the setup checklist first.')
    calc=plan(p)
    if not calc['eligible']: raise HTTPException(422,'Risk budget cannot support minimum size, or costs exceed reward.')
    with db() as c:
        for row in c.execute("SELECT payload FROM records WHERE kind='trade'"):
            if json.loads(row['payload']).get('status')=='Open': raise HTTPException(409,'Close the existing paper position first.')
    data={**p.model_dump(),**calc,'status':'Open','source':'sample','strategy':'breakout-retest-v0-unproven'}
    return {'id':record('trade',data),**data}

class Observation(BaseModel):
    note: str=Field(min_length=1,max_length=2000)
@app.post('/api/observations')
def observation(p:Observation): return {'id':record('observation',p.model_dump())}
@app.get('/api/journal')
def journal():
    with db() as c: return [dict(id=r['id'],created=r['created'],kind=r['kind'],**json.loads(r['payload'])) for r in c.execute('SELECT * FROM records ORDER BY id DESC')]

class Close(BaseModel):
    price: float=Field(gt=0,le=10000000)
@app.post('/api/trades/{ident}/close')
def close(ident:int,p:Close):
    with db() as c:
        r=c.execute("SELECT * FROM records WHERE id=? AND kind='trade'",(ident,)).fetchone()
        if not r: raise HTTPException(404,'Paper trade not found')
        d=json.loads(r['payload'])
        if d['status']!='Open': raise HTTPException(409,'Already closed')
        gross=(p.price-d['entry'])*(1 if d['side']=='buy' else -1)*d['lots']
        d.update(status='Closed',closed_at=time.time(),exit=p.price,pnl=round(gross-d['lots']*(d['spread']+2*d['slippage']),2))
        c.execute('UPDATE records SET payload=? WHERE id=?',(json.dumps(d),ident))
        return d

@app.get('/api/market')
def market(tf:Literal['M5','M15','H1','H4']='M5',step:int=0,source:Literal['sample','exness']='sample',symbol:Literal['BTCUSDm','XAUUSDm']='BTCUSDm'):
    if source=='sample' and symbol!='BTCUSDm': return dict(source='sample',connected=False,candles=[],symbol=symbol,state='unsupported',message='Gold uses its own Exness demo feed; synthetic BTC replay is unavailable for Gold.')
    if source=='sample':
        step=max(0,min(step,200)); bars=candles(tf,step)
        return dict(source='sample',connected=False,candles=bars,price=bars[-1]['close'],balance=1000,symbol='BTCUSDm',step=step)
    prefix='btc' if symbol=='BTCUSDm' else 'xau'
    history=read_history(BRIDGE_PATH.with_name(prefix+'-studio-candles.json'),expected_symbol=symbol)
    if history['state']!='valid': return dict(source='exness',connected=False,candles=[],symbol=symbol,message=('Waiting for GoldStudioQuotes on an XAUUSDm demo chart in MT5.' if symbol=='XAUUSDm' and history['state']=='missing' else history['message']),state=history['state'])
    data=history['data']; quote=bridge_status() if symbol=='BTCUSDm' else bridge_status(BRIDGE_PATH.with_name('xau-studio-quotes.json'),expected_symbol=symbol)
    fresh=0<=history['age_seconds']<15 and data.get('demo') is True and data.get('terminal_connected') is True and quote['connected']
    bars=data['candles'].get(tf,[])
    if not bars:return dict(source='exness',connected=False,state='missing-timeframe',candles=[],symbol=data['symbol'],message='H4 candles are not arriving yet. Reload the updated BTCStudioQuotes indicator in MT5.')
    tick_seconds=quote.get('snapshot',{}).get('tick_time_msc',0)/1000
    recent_bars=bool(bars) and 0<=tick_seconds-bars[-1]['time']<{**INTERVALS,'H4':14400}[tf]*2
    fresh=fresh and recent_bars
    if fresh: archive(data,DB)
    return dict(source='exness',connected=fresh and len(bars)>1,state='fresh' if fresh else 'stale',candles=bars,price=bars[-1]['close'] if bars else None,symbol=data['symbol'],clock='broker-server',age_seconds=history['age_seconds'],research_m1_count=len(data['candles']['M1']),message='Exness demo candles · Broker server time · Last candle forming' if fresh else 'Feed stale or disconnected. Displayed candles are last received; not entry confirmation.')

BRIDGE_PATH = Path(os.environ.get('BTC_STUDIO_QUOTE_PATH', str(Path.home() / 'Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/users/user/AppData/Roaming/MetaQuotes/Terminal/Common/Files/btc-studio-quotes.json')))

def bridge_status(path=None, now=None, expected_symbol='BTCUSDm'):
    path = Path(path) if path is not None else BRIDGE_PATH
    now = time.time() if now is None else now
    base = dict(connected=False, source='exness-mt5', chart_source='sample')
    if not path.exists():
        return {**base, 'state':'missing', 'message':'Waiting for the BTC Studio Quotes indicator in MT5. Chart remains sample data.'}
    try:
        data=json.loads(path.read_text())
        numeric=('timestamp','bid','ask','contract_size','volume_min','volume_step','quote_age_seconds')
        if any(type(data.get(k)) not in (int,float) or not math.isfinite(data[k]) for k in numeric):
            raise ValueError('Invalid quote fields')
        if data.get('version')!=1 or data.get('symbol')!=expected_symbol or data['ask']<data['bid'] or data['bid']<=0 or any(data[k]<=0 for k in ('contract_size','volume_min','volume_step')):
            raise ValueError('Invalid quote specifications')
        age=now-data['timestamp']
        fresh=0<=age<15 and 0<=data['quote_age_seconds']<15
        connected=fresh and data.get('terminal_connected') is True and data.get('demo') is True
        state='fresh' if connected else ('non-demo' if data.get('demo') is not True else 'stale')
        return {**base,'connected':connected,'state':state,'age_seconds':round(age,1),'snapshot':data,'spread':round(data['ask']-data['bid'],8),'message':'Fresh demo quote received. Chart source is selected separately; paper sizing remains illustrative.' if connected else 'Quote is stale, terminal is disconnected, or demo account is not verified. Broker candles must not be used as fresh confirmation.'}
    except (OSError,ValueError,TypeError):
        return {**base,'state':'invalid','message':'Quote file is unavailable or incomplete; waiting for the next valid update.'}

@app.get('/api/bridge')
def bridge(symbol:Literal['BTCUSDm','XAUUSDm']='BTCUSDm'): return bridge_status() if symbol=='BTCUSDm' else bridge_status(BRIDGE_PATH.with_name('xau-studio-quotes.json'),expected_symbol=symbol)

class ResearchConfig(BaseModel):
    commission_per_lot_side: float=Field(ge=0,le=10000)
    commission_confirmed: bool=False
    commission_source: str=Field(min_length=1,max_length=500)
    parity_verified: bool=False
    verification_note: str=Field(min_length=1,max_length=1000)
class EngineControl(BaseModel):
    action: Literal['start','pause','news','resume']
class LevelRequest(BaseModel):
    price: float=Field(gt=0,le=10000000)
    side: Literal['support','resistance']
    touches: list[int]
    context_reviewed: bool=False

def research_call(fn):
    try:return fn()
    except ValueError as exc:raise HTTPException(422,str(exc))
@app.get('/api/engine')
def engine_status(): return paper().status()
@app.post('/api/engine/config')
def engine_config(p:ResearchConfig):
    research_call(lambda:paper().configure(p.model_dump()));return paper().status()
@app.post('/api/engine/control')
def engine_control(p:EngineControl):
    research_call(lambda:paper().control(p.action));return paper().status()
@app.get('/api/engine/evidence')
def engine_evidence(price:float,side:Literal['support','resistance']):
    if not math.isfinite(price) or price<=0:raise HTTPException(422,'Invalid level price')
    bars,q,ready=paper().source()
    return {'ready':ready,'evidence':engine.evidence(bars.get('M15',[]),price,side) if ready else []}
@app.post('/api/engine/levels')
def engine_level(p:LevelRequest):return research_call(lambda:paper().register(p.price,p.side,p.touches,p.context_reviewed))
@app.post('/api/engine/levels/{ident}/cancel')
def engine_cancel(ident:str):
    research_call(lambda:paper().cancel(ident));return paper().status()
@app.get('/api/engine/export')
def engine_export():
    with paper().connection() as c: audit=[json.loads(r['payload']) for r in c.execute('SELECT payload FROM paper_audit ORDER BY id')]
    return {'parameters':engine.P,'manifest':engine.MANIFEST,'state':paper().status(),'audit':audit}

# Journal is separate from execution and contains no broker write APIs.
from . import journaling
from datetime import datetime, timezone
from pydantic import model_validator, ConfigDict
class JournalTrade(BaseModel):
    model_config=ConfigDict(allow_inf_nan=False)
    symbol: str=Field(min_length=1,max_length=30,pattern=r'^[A-Za-z0-9._-]+$')
    side: Literal['buy','sell']
    lots: float=Field(gt=0,le=100000)
    entry: float=Field(gt=0,le=100000000)
    exit: float=Field(gt=0,le=100000000)
    opened_at: datetime
    closed_at: datetime
    pnl: float=Field(ge=-100000000,le=100000000)
    strategy: str=Field(default='',max_length=100)
    note: str=Field(default='',max_length=4000)
    @model_validator(mode='after')
    def valid_times(self):
        if self.opened_at.tzinfo is None or self.closed_at.tzinfo is None:raise ValueError('Include timezone in trade timestamps')
        if self.closed_at<self.opened_at:raise ValueError('Close must be at or after open')
        if self.closed_at>datetime.now(timezone.utc):raise ValueError('Closed trades cannot be dated in the future')
        return self
    def journal_payload(self):
        return {**self.model_dump(exclude={'opened_at','closed_at'}),'opened_at':self.opened_at.timestamp(),'closed_at':self.closed_at.timestamp(),'status':'closed','symbol':self.symbol.upper()}
class JournalNote(BaseModel):
    source: Literal['manual','engine','sample','mt5']
    day: str
    note: str=Field(max_length=4000)
class JournalBalance(BaseModel):
    model_config=ConfigDict(allow_inf_nan=False)
    initial_balance: float=Field(ge=0,le=100000000)
@app.get('/api/trading-journal')
def trading_journal(source:Literal['manual','engine','sample','mt5']='manual',month:str=''):
    if source=='mt5': mt5_journal.sync(DB,BRIDGE_PATH.with_name('studio-trades.json'))
    return research_call(lambda:journaling.snapshot(DB,source,month or datetime.now(journaling.TZ).strftime('%Y-%m')))
@app.post('/api/trading-journal/trades')
def add_journal_trade(p:JournalTrade):return {'id':journaling.add_trade(DB,p.journal_payload())}
@app.put('/api/trading-journal/trades/{ident}')
def edit_journal_trade(ident:str,p:JournalTrade):return {'id':research_call(lambda:journaling.add_trade(DB,p.journal_payload(),ident))}
@app.delete('/api/trading-journal/trades/{ident}')
def delete_journal_trade(ident:str):
    with journaling.connect(DB) as c:
        if not c.execute('SELECT 1 FROM journal_trades WHERE id=?',(ident,)).fetchone():raise HTTPException(404,'Manual trade not found')
        c.execute('DELETE FROM journal_trades WHERE id=?',(ident,))
    return {'deleted':True}
@app.post('/api/trading-journal/notes')
def journal_note(p:JournalNote):
    research_call(lambda:journaling.save_note(DB,p.source,p.day,p.note));return {'saved':True}
@app.post('/api/trading-journal/balance')
def journal_balance(p:JournalBalance):
    journaling.set_balance(DB,p.initial_balance);return {'saved':True}

from . import journal_review
class ChartReviewRequest(BaseModel):
    trade_id: Optional[str]=Field(default=None,max_length=100)
    source: Literal['manual','engine','sample','mt5']
    day: str
    symbol: str=Field(default='BTCUSDm',min_length=1,max_length=30)
    timeframe: Literal['M5','M15','H1']='M5'
@app.get('/api/trading-journal/chart-review')
def chart_review(source:Literal['manual','engine','sample','mt5'],day:str,symbol:str='BTCUSDm',timeframe:Literal['M5','M15','H1']='M5',trade_id:Optional[str]=None):
    if trade_id:return research_call(lambda:journal_review.trade_review(DB,source,day,trade_id,timeframe))
    return research_call(lambda:journal_review.load(DB,source,day,symbol,timeframe))
@app.post('/api/trading-journal/chart-review')
def save_chart_review(p:ChartReviewRequest):
    if p.trade_id:return research_call(lambda:journal_review.trade_review(DB,p.source,p.day,p.trade_id,p.timeframe,save=True))
    return research_call(lambda:journal_review.capture(DB,p.source,p.day,p.symbol,p.timeframe))

@app.get('/api/trading-journal/mt5-status')
def mt5_journal_status():
    result=mt5_journal.sync(DB,BRIDGE_PATH.with_name('studio-trades.json'))
    today=datetime.now(journaling.TZ).date().isoformat()
    with journaling.connect(DB) as c:
        closed=[t for t in journaling.records(c) if t['source']=='mt5' and t['status']=='closed' and t.get('closed_at') is not None and journaling.day(t['closed_at'])==today]
    result.update(closed_today=journaling.money(t['pnl'] for t in closed),journal_day=today)
    return {k:v for k,v in result.items() if k not in ('account','hash')}

# Postmortems are isolated from execution. Outbound AI is opt-in per request.
from . import trade_postmortem
class TradeReviewPlan(BaseModel):
    source: Literal['manual','engine','sample','mt5']
    trade_id: str=Field(min_length=1,max_length=100)
    plan: trade_postmortem.Plan
class TradeReviewAction(BaseModel):
    source: Literal['manual','engine','sample','mt5']
    trade_id: str=Field(min_length=1,max_length=100)
class TradeReviewAI(TradeReviewAction):
    consent: bool=False
    fingerprint: str=Field(min_length=64,max_length=64)
@app.get('/api/trading-journal/postmortem')
def get_postmortem(source:Literal['manual','engine','sample','mt5'],trade_id:str):
    return research_call(lambda:trade_postmortem.review(DB,source,trade_id))
@app.post('/api/trading-journal/postmortem/plan')
def save_postmortem_plan(p:TradeReviewPlan):
    return research_call(lambda:trade_postmortem.save_plan(DB,p.source,p.trade_id,p.plan.model_dump()))
@app.post('/api/trading-journal/postmortem/local')
def save_postmortem_local(p:TradeReviewAction):
    return research_call(lambda:trade_postmortem.save_local(DB,p.source,p.trade_id))
@app.post('/api/trading-journal/postmortem/ai')
def generate_postmortem_ai(p:TradeReviewAI):
    return research_call(lambda:trade_postmortem.generate(DB,p.source,p.trade_id,p.consent,p.fingerprint))

from . import trade_ideas
class IdeaRequest(BaseModel):
    source: Literal['manual','engine','sample','mt5']
    plan: trade_ideas.Plan
class IdeaLink(BaseModel):
    source: Literal['manual','engine','sample','mt5']
    trade_id: str=Field(min_length=1,max_length=100)
    idea_id: Optional[str]=Field(default=None,max_length=100)
@app.get('/api/trading-journal/ideas')
def journal_ideas(source:Literal['manual','engine','sample','mt5']):
    return research_call(lambda:trade_ideas.listing(DB,source))
@app.post('/api/trading-journal/ideas')
def new_journal_idea(p:IdeaRequest):
    return {'id':research_call(lambda:trade_ideas.create(DB,p.source,p.plan.model_dump()))}
@app.post('/api/trading-journal/ideas/link')
def link_journal_idea(p:IdeaLink):
    research_call(lambda:trade_ideas.assign(DB,p.source,p.trade_id,p.idea_id));return {'saved':True}
