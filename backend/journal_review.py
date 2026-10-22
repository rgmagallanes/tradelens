"""Read-only historical context and immutable day-review captures; no order APIs."""
import hashlib,json,sqlite3,time
from datetime import date,datetime,time as daytime,timedelta
from functools import lru_cache
from pathlib import Path
from . import journaling
from .history import read_history
HISTORY_PATH=Path(__file__).resolve().parents[1]/'research/exness-history-volume-2026-10-19.json'
INTERVALS={'M5':300,'M15':900,'H1':3600}

def connection(path):
    c=sqlite3.connect(path,timeout=10);c.row_factory=sqlite3.Row
    c.execute('CREATE TABLE IF NOT EXISTS journal_chart_snapshots(source TEXT,day TEXT,symbol TEXT,timeframe TEXT,payload TEXT NOT NULL,PRIMARY KEY(source,day,symbol,timeframe))');c.commit();return c

def validate(source,d,symbol,tf):
    if source not in journaling.SOURCES or tf not in INTERVALS:raise ValueError('Invalid chart source or timeframe')
    if date.fromisoformat(d).isoformat()!=d:raise ValueError('Use YYYY-MM-DD for the review date')
    if not symbol or len(symbol)>30 or any(not(ch.isascii() and (ch.isalnum() or ch in '._-')) for ch in symbol):raise ValueError('Invalid chart symbol')
    return symbol.upper()

@lru_cache(maxsize=2)
def imported(path,mtime):
    h=read_history(Path(path),max_bars=200000)
    d=h.get('data',{})
    return d if h['state']=='valid' and d.get('demo') is True and d.get('server_utc_offset_seconds')==0 else {}

def load(path,source,d,symbol='BTCUSDm',tf='M5',now=None):
    symbol=validate(source,d,symbol,tf)
    with connection(path) as c:
        r=c.execute('SELECT payload FROM journal_chart_snapshots WHERE source=? AND day=? AND symbol=? AND timeframe=?',(source,d,symbol,tf)).fetchone()
        if r:return {**json.loads(r['payload']),'saved':True}
    return reconstruct(path,source,d,symbol,tf,now)

def reconstruct(path,source,d,symbol,tf,now=None):
    now=time.time() if now is None else now
    base=dict(source=source,day=d,symbol=symbol,timeframe=tf,saved=False,bars=[],trades=[],capture_kind='historical_reconstruction',timezone='Asia/Manila',state='unavailable')
    if source=='sample':return {**base,'message':'No chart was recorded with these sample replay trades. Broker candles cannot represent synthetic replay prices.'}
    if symbol not in ('BTCUSDM','XAUUSDM'):return {**base,'message':'No recorded chart history for this symbol. Only BTCUSDm and XAUUSDm demo candle archives are supported.'}
    start=int(datetime.combine(date.fromisoformat(d),daytime(),journaling.TZ).timestamp());end=start+86400;interval=INTERVALS[tf];bars={};provenance=[]
    if HISTORY_PATH and HISTORY_PATH.exists():
        data=imported(str(HISTORY_PATH),HISTORY_PATH.stat().st_mtime_ns)
        if data.get('symbol','').upper()==symbol:
            selected=[b for b in data.get('candles',{}).get(tf,[]) if b['closed'] and start<=b['time']<end and b['time']+interval<=now]
            bars.update({b['time']:{k:b[k] for k in ('time','open','high','low','close')} for b in selected})
            if selected:provenance.append('Saved MT5 demo export: '+HISTORY_PATH.name)
    with journaling.connect(path) as c:
        exists=c.execute("SELECT 1 FROM sqlite_master WHERE name='broker_candles' AND type='table'").fetchone()
        if exists:
            rows=c.execute('SELECT broker_time,open,high,low,close FROM broker_candles WHERE UPPER(symbol)=? AND timeframe=? AND closed=1 AND broker_time>=? AND broker_time<? AND broker_time+?<=? ORDER BY broker_time',(symbol,tf,start,end,interval,now)).fetchall()
            for r in rows:bars[r['broker_time']]=dict(time=r['broker_time'],open=r['open'],high=r['high'],low=r['low'],close=r['close'])
            if rows:provenance.append('Local MT5 demo candle archive')
    values=sorted(bars.values(),key=lambda b:b['time'])
    trades=[t for day in journaling.snapshot(path,source,d[:7])['days'] if day['date']==d for t in day['trades'] if t['symbol'].upper()==symbol]
    expected_completed=max(0,(min(end,int(now)//interval*interval)-start)//interval)
    coverage=dict(bars=len(values),expected_full_day=86400//interval,missing_completed_bars=max(0,expected_completed-len(values)),in_progress=now<end)
    if len(values)<2:return {**base,'coverage':coverage,'message':'No usable recorded candles for this day yet. Keep the MT5 exporter and local app running to collect history.'}
    return {**base,'state':'available','bars':values,'trades':trades,'coverage':coverage,'provenance':provenance,'captured_at':now,'message':'Historical chart reconstruction from Exness demo candles; not an entry-time screenshot or proof of execution.','time_basis':'MT5 UTC+0, displayed in Asia/Manila (UTC+8)'}

def capture(path,source,d,symbol='BTCUSDm',tf='M5',now=None):
    symbol=validate(source,d,symbol,tf)
    data=load(path,source,d,symbol,tf,now)
    if data.get('saved'):return data
    if data['state']!='available':raise ValueError(data['message'])
    data['snapshot_sha256']=hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    with connection(path) as c:
        c.execute('INSERT OR IGNORE INTO journal_chart_snapshots VALUES(?,?,?,?,?)',(source,d,symbol,tf,json.dumps(data)))
        saved=c.execute('SELECT payload FROM journal_chart_snapshots WHERE source=? AND day=? AND symbol=? AND timeframe=?',(source,d,symbol,tf)).fetchone()
    return {**json.loads(saved['payload']),'saved':True}

# Separate keys keep one trade's frozen chart context from replacing another's.
def trade_review(path,source,d,trade_id,tf='M5',save=False,now=None):
    if not isinstance(trade_id,str) or not 1<=len(trade_id)<=100:raise ValueError('Invalid trade identifier')
    with journaling.connect(path) as c:
        trade=next((t for t in journaling.records(c) if t['source']==source and t['id']==trade_id),None)
    if not trade:raise ValueError('Trade not found in selected journal source')
    symbol=validate(source,d,trade['symbol'],tf)
    with connection(path) as c:
        c.execute('CREATE TABLE IF NOT EXISTS journal_trade_chart_snapshots(source TEXT,trade_id TEXT,timeframe TEXT,payload TEXT NOT NULL,PRIMARY KEY(source,trade_id,timeframe))')
        row=c.execute('SELECT payload FROM journal_trade_chart_snapshots WHERE source=? AND trade_id=? AND timeframe=?',(source,trade_id,tf)).fetchone()
        if row:return {**json.loads(row[0]),'saved':True}
    data=reconstruct(path,source,d,symbol,tf,now)
    data.update(trade_id=trade_id,trades=[trade])
    if not save:return data
    if data['state']!='available':raise ValueError(data['message'])
    data['snapshot_sha256']=hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    with connection(path) as c:
        c.execute('INSERT OR IGNORE INTO journal_trade_chart_snapshots VALUES(?,?,?,?)',(source,trade_id,tf,json.dumps(data)))
        row=c.execute('SELECT payload FROM journal_trade_chart_snapshots WHERE source=? AND trade_id=? AND timeframe=?',(source,trade_id,tf)).fetchone()
    return {**json.loads(row[0]),'saved':True}
