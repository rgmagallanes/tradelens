"""Local journal projection. Reads paper records; never controls execution."""
import calendar,json,sqlite3,uuid
from datetime import date,datetime,time,timezone,timedelta
from decimal import Decimal
TZ=timezone(timedelta(hours=8))
SOURCES=('manual','engine','sample','mt5')

def connect(path):
    c=sqlite3.connect(path,timeout=10);c.row_factory=sqlite3.Row
    c.execute('CREATE TABLE IF NOT EXISTS journal_trades(id TEXT PRIMARY KEY,payload TEXT NOT NULL)')
    c.execute('CREATE TABLE IF NOT EXISTS journal_notes(source TEXT,day TEXT,note TEXT,PRIMARY KEY(source,day))')
    c.execute('CREATE TABLE IF NOT EXISTS journal_settings(source TEXT PRIMARY KEY,initial_balance REAL NOT NULL)')
    c.commit();return c

def day(stamp):return datetime.fromtimestamp(stamp,TZ).date().isoformat()
def money(values):return float(sum((Decimal(str(v)) for v in values),Decimal('0')).quantize(Decimal('.01')))
def records(c):
    tables={r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    out=[]
    for r in c.execute('SELECT id,payload FROM journal_trades'):
        out.append(dict(json.loads(r['payload']),id=r['id'],source='manual'))
    if 'mt5_journal_trades' in tables:
        out.extend(json.loads(r[0]) for r in c.execute('SELECT payload FROM mt5_journal_trades'))
    if 'records' in tables:
        for row in c.execute("SELECT * FROM records WHERE kind='trade'"):
            r=json.loads(row['payload'])
            out.append(dict(id='sample-'+str(row['id']),source='sample',symbol='BTCUSDm',side=r['side'],lots=r['lots'],entry=r['entry'],exit=r.get('exit'),opened_at=row['created'],closed_at=r.get('closed_at'),status='closed' if r['status']=='Closed' else 'open',pnl=r.get('pnl'),strategy=r.get('strategy','Sample replay'),note=r.get('note','')))
    if 'paper_engine' in tables:
        row=c.execute('SELECT payload FROM paper_engine WHERE id=1').fetchone()
        if row:
            state=json.loads(row[0])
            for r in state.get('closed',[])+([state['position']] if state.get('position') else []):
                out.append(dict(id='engine-'+r['id'],source='engine',symbol='BTCUSDm',side=r['side'],lots=r['lots'],entry=r['entry'],exit=r.get('exit'),opened_at=r['opened_at'],closed_at=r.get('closed_at'),status='closed' if r.get('closed_at') is not None else 'open',pnl=r.get('pnl'),strategy='Breakout + retest v1',note='',stop=r.get('stop'),target=r.get('target'),uncertainty=r.get('uncertainty',False)))
    return out

def snapshot(path,source,month):
    if source not in SOURCES:raise ValueError('Unknown journal source')
    try:
        first=date.fromisoformat(month+'-01');last=date(first.year,first.month,calendar.monthrange(first.year,first.month)[1])
    except (ValueError,TypeError):raise ValueError('Use a valid YYYY-MM month')
    with connect(path) as c:
        trades=[r for r in records(c) if r['source']==source]
        row=c.execute('SELECT initial_balance FROM journal_settings WHERE source=?',(source,)).fetchone()
        initial=float(row[0]) if row else (0. if source in ('manual','mt5') else 1000.)
        notes={r['day']:r['note'] for r in c.execute('SELECT day,note FROM journal_notes WHERE source=?',(source,))}
    known=[r for r in trades if r['status']=='closed' and r['closed_at'] is not None]
    balance=money([initial]+[r['pnl'] for r in known if day(r['closed_at'])<first.isoformat()]);days=[]
    for n in range(1,last.day+1):
        d=date(first.year,first.month,n).isoformat()
        closed=[r for r in known if day(r['closed_at'])==d]
        opened=[r for r in trades if r['status']=='open' and day(r['opened_at'])==d]
        pnl=money(r['pnl'] for r in closed);end=money([balance,pnl])
        days.append(dict(date=d,start_balance=balance,pnl=pnl,end_balance=end,closed_count=len(closed),open_count=len(opened),wins=sum(r['pnl']>0 for r in closed),losses=sum(r['pnl']<0 for r in closed),trades=sorted(closed+opened,key=lambda r:r.get('closed_at') or r['opened_at']),note=notes.get(d,'')))
        balance=end
    closed=[r for r in known if first.isoformat()<=day(r['closed_at'])<=last.isoformat()]
    pnl=money(r['pnl'] for r in closed)
    return dict(source=source,month=month,timezone='Asia/Manila',currency='USD',initial_balance=initial,days=days,summary=dict(pnl=pnl,closed_count=len(closed),wins=sum(r['pnl']>0 for r in closed),losses=sum(r['pnl']<0 for r in closed),win_rate=sum(r['pnl']>0 for r in closed)/len(closed) if closed else None,start_balance=days[0]['start_balance'],end_balance=balance),open_positions=[r for r in trades if r['status']=='open'],undated_trades=[r for r in trades if r['status']=='closed' and r['closed_at'] is None],first_trade_date=min((day(r['opened_at']) for r in trades),default=None))

def add_trade(path,payload,ident=None):
    with connect(path) as c:
        if ident and not c.execute('SELECT 1 FROM journal_trades WHERE id=?',(ident,)).fetchone():raise ValueError('Manual trade not found')
        ident=ident or 'manual-'+uuid.uuid4().hex
        c.execute('INSERT OR REPLACE INTO journal_trades VALUES(?,?)',(ident,json.dumps(payload)))
    return ident

def save_note(path,source,d,note):
    if source not in SOURCES:raise ValueError('Unknown journal source')
    if date.fromisoformat(d).isoformat()!=d:raise ValueError('Invalid date')
    with connect(path) as c:c.execute('INSERT OR REPLACE INTO journal_notes VALUES(?,?,?)',(source,d,note))

def set_balance(path,balance):
    with connect(path) as c:c.execute('INSERT OR REPLACE INTO journal_settings VALUES(?,?)',('manual',balance))

# User-authored review metadata never changes an imported execution.
def tags(path,source,trade_id=None,mistakes=None,lessons=None):
    if source not in SOURCES:raise ValueError('Unknown journal source')
    with connect(path) as c:
        c.execute('CREATE TABLE IF NOT EXISTS journal_review_tags(source TEXT,trade_id TEXT,payload TEXT,PRIMARY KEY(source,trade_id))')
        if trade_id is not None:
            matched=next((t for t in records(c) if t['source']==source and t['id']==trade_id),None)
            if not matched:raise ValueError('Trade not found in this journal source')
            if matched.get('status')!='closed':raise ValueError('Review tags are available after the trade closes')
            def clean(values):
                if not isinstance(values,list) or len(values)>8:raise ValueError('Use at most eight tags per category')
                if any(not isinstance(v,str) or not 1<=len(v.strip())<=60 for v in values):raise ValueError('Tags must contain 1 to 60 characters')
                return list(dict.fromkeys(v.strip().lower() for v in values))
            payload=dict(mistakes=clean(mistakes),lessons=clean(lessons))
            c.execute('INSERT OR REPLACE INTO journal_review_tags VALUES(?,?,?)',(source,trade_id,json.dumps(payload)))
            return {'saved':True}
        return {'tags':{row['trade_id']:json.loads(row['payload']) for row in c.execute('SELECT trade_id,payload FROM journal_review_tags WHERE source=?',(source,))}}
