"""Immutable trade plans and source-isolated execution grouping. No order APIs."""
import hashlib,json,sqlite3,time,uuid
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,model_validator
from . import journaling
class Plan(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
    title:str=Field(min_length=1,max_length=100)
    symbol:str=Field(min_length=1,max_length=30,pattern=r'^[A-Za-z0-9._-]+$')
    side:Literal['buy','sell']
    setup:str=Field(min_length=1,max_length=100)
    reason:str=Field(min_length=1,max_length=2000)
    entry:float=Field(gt=0,le=1e8)
    stop:float=Field(gt=0,le=1e8)
    target:float=Field(gt=0,le=1e8)
    risk_budget:float=Field(gt=0,le=1e8)
    @model_validator(mode='after')
    def levels(self):
        if not self.title.strip() or not self.setup.strip() or not self.reason.strip():raise ValueError('Title, setup and entry reason are required')
        if not (self.stop<self.entry<self.target if self.side=='buy' else self.target<self.entry<self.stop):raise ValueError('Stop and target must be on the correct sides of planned entry')
        return self

def connection(path):
    c=journaling.connect(path)
    c.execute('CREATE TABLE IF NOT EXISTS journal_ideas(id TEXT PRIMARY KEY,source TEXT NOT NULL,created_at REAL NOT NULL,plan TEXT NOT NULL,snapshot TEXT NOT NULL)')
    c.execute('CREATE TABLE IF NOT EXISTS journal_idea_links(source TEXT,execution_key TEXT,idea_id TEXT,assigned_at REAL,PRIMARY KEY(source,execution_key))')
    c.execute('CREATE TABLE IF NOT EXISTS journal_idea_link_audit(id INTEGER PRIMARY KEY,source TEXT,execution_key TEXT,old_idea TEXT,new_idea TEXT,changed_at REAL)')
    c.commit();return c

def key(t):
    return 'position:'+str(t['position_id']) if t['source']=='mt5' and t.get('position_id') else 'trade:'+t['id']

def context(c,symbol,now):
    bars=[]
    if c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='broker_candles'").fetchone():
        rows=c.execute('SELECT broker_time,open,high,low,close FROM broker_candles WHERE UPPER(symbol)=? AND timeframe=? AND closed=1 AND broker_time+300<=? ORDER BY broker_time DESC LIMIT 60',(symbol.upper(),'M5',now)).fetchall()
        bars=[dict(time=r[0],open=r[1],high=r[2],low=r[3],close=r[4]) for r in reversed(rows)]
    data=dict(kind='saved_plan_time_candle_context',captured_at=now,symbol=symbol,timeframe='M5',bars=bars,last_candle_age_seconds=max(0,now-bars[-1]['time']-300) if bars else None,provenance='Local MT5 demo candle archive; completed bars only. Not a screenshot or proof of execution; manual trades may use another feed.')
    data['sha256']=hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest();return data

def create(path,source,plan,now=None):
    if source not in journaling.SOURCES:raise ValueError('Unknown source')
    p=Plan.model_validate(plan).model_dump();now=time.time() if now is None else now;ident='idea-'+uuid.uuid4().hex
    with connection(path) as c:
        snap=context(c,p['symbol'],now) if source!='sample' else dict(kind='unavailable',captured_at=now,bars=[],provenance='No source-faithful sample chart capture is configured. Broker candles are not substituted.')
        c.execute('INSERT INTO journal_ideas VALUES(?,?,?,?,?)',(ident,source,now,json.dumps(p),json.dumps(snap)))
    return ident

def assign(path,source,trade_id,idea_id,now=None):
    if source not in journaling.SOURCES:raise ValueError('Unknown source')
    now=time.time() if now is None else now
    with connection(path) as c:
        c.execute('BEGIN IMMEDIATE')
        t=next((t for t in journaling.records(c) if t['source']==source and t['id']==trade_id),None)
        if not t:raise ValueError('Execution not found in selected source')
        if idea_id:
            row=c.execute('SELECT source,plan FROM journal_ideas WHERE id=?',(idea_id,)).fetchone()
            if not row or row['source']!=source:raise ValueError('Trading idea not found in this source')
            p=json.loads(row['plan'])
            if p['symbol'].upper()!=t['symbol'].upper() or p['side']!=t['side']:raise ValueError('Group only the same symbol and direction; create a separate idea for a hedge')
        execution_key=key(t);old=c.execute('SELECT idea_id FROM journal_idea_links WHERE source=? AND execution_key=?',(source,execution_key)).fetchone();old=old[0] if old else None
        if old==idea_id:return
        if idea_id:c.execute('INSERT OR REPLACE INTO journal_idea_links VALUES(?,?,?,?)',(source,execution_key,idea_id,now))
        else:c.execute('DELETE FROM journal_idea_links WHERE source=? AND execution_key=?',(source,execution_key))
        c.execute('INSERT INTO journal_idea_link_audit(source,execution_key,old_idea,new_idea,changed_at) VALUES(?,?,?,?,?)',(source,execution_key,old,idea_id,now))

def plan_timing(created,trades):
    if not trades:return 'Saved plan · awaiting execution'
    return 'Saved before all linked entries' if created<=min(t['opened_at'] for t in trades) else 'Retrospective for one or more entries'

def linked_plan(path,source,t):
    with connection(path) as c:
        r=c.execute('SELECT i.created_at,i.plan FROM journal_idea_links l JOIN journal_ideas i ON i.id=l.idea_id WHERE l.source=? AND l.execution_key=? AND i.source=?',(source,key(t),source)).fetchone()
    if not r:return None
    return dict(created_at=r['created_at'],timing=plan_timing(r['created_at'],[t]),immutable=True,plan=json.loads(r['plan']))

def listing(path,source,now=None):
    if source not in journaling.SOURCES:raise ValueError('Unknown source')
    now=time.time() if now is None else now
    with connection(path) as c:
        trades=[t for t in journaling.records(c) if t['source']==source]
        links={r['execution_key']:r['idea_id'] for r in c.execute('SELECT execution_key,idea_id FROM journal_idea_links WHERE source=?',(source,))}
        rows=c.execute('SELECT * FROM journal_ideas WHERE source=? ORDER BY created_at DESC',(source,)).fetchall()
        stamp=None
        if source=='mt5' and c.execute("SELECT 1 FROM sqlite_master WHERE name='mt5_journal_meta'").fetchone():
            r=c.execute('SELECT payload FROM mt5_journal_meta WHERE id=1').fetchone();stamp=json.loads(r[0]).get('timestamp') if r else None
    def totals(items):
        closed=[t for t in items if t['status']=='closed'];opened=[t for t in items if t['status']=='open'];known=[t for t in opened if isinstance(t.get('floating_pnl'),(int,float))]
        return dict(closed_net=journaling.money(t.get('pnl') or 0 for t in closed),closed_rows=len(closed),open_rows=len(opened),closed_lots=sum(t['lots'] for t in closed),open_lots=sum(t['lots'] for t in opened),floating_pnl=journaling.money(t['floating_pnl'] for t in known) if len(known)==len(opened) and source=='mt5' else None)
    ideas=[]
    for r in rows:
        items=sorted([t for t in trades if links.get(key(t))==r['id']],key=lambda t:(t['opened_at'],t['id']))
        ideas.append(dict(id=r['id'],source=source,created_at=r['created_at'],plan=json.loads(r['plan']),snapshot=json.loads(r['snapshot']),timing=plan_timing(r['created_at'],items),positions=len({key(t) for t in items}),status='open' if any(t['status']=='open' for t in items) else 'closed' if items else 'planned',trades=items,**totals(items)))
    bykey={}
    for t in trades:
        k=key(t)
        if k not in links:bykey.setdefault(k,[]).append(t)
    ungrouped=[dict(key=k,symbol=items[0]['symbol'],side=items[0]['side'],opened_at=min(t['opened_at'] for t in items),trades=items,**totals(items)) for k,items in bykey.items()]
    return dict(source=source,ideas=ideas,ungrouped=sorted(ungrouped,key=lambda g:g['opened_at'],reverse=True),snapshot_timestamp=stamp,floating_fresh=bool(stamp and 0<=now-stamp<30),note='All dates in this source. MT5 partial exits and open remainder follow the same position automatically. Group P/L is a view of the same executions, not extra journal entries.')
