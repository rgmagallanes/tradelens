"""Read-only MT5 demo/live deal ingestion. No execution APIs; account-isolated, idempotent ledger."""
import hashlib,json,math,sqlite3,time
from pathlib import Path

def connection(path):
 c=sqlite3.connect(path,timeout=10);c.row_factory=sqlite3.Row
 c.execute('CREATE TABLE IF NOT EXISTS mt5_journal_meta(id INTEGER PRIMARY KEY CHECK(id=1),payload TEXT NOT NULL)')
 c.execute('CREATE TABLE IF NOT EXISTS mt5_journal_deals(ticket TEXT PRIMARY KEY,payload TEXT NOT NULL)')
 c.execute('CREATE TABLE IF NOT EXISTS mt5_journal_trades(id TEXT PRIMARY KEY,payload TEXT NOT NULL)')
 c.execute('CREATE TABLE IF NOT EXISTS mt5_journal_protection(position_id TEXT,observed_at REAL,payload TEXT,PRIMARY KEY(position_id,observed_at))')
 c.commit();return c

def number(value,positive=False):
 if type(value) not in (int,float) or not math.isfinite(value) or (positive and value<=0):raise ValueError('Invalid numeric trade field')
 return value

def ident(value):
 if not isinstance(value,str) or not value.isdigit() or len(value)>24 or int(value)<=0:raise ValueError('Invalid MT5 identifier')
 return value

def validate(d,now):
 if not isinstance(d,dict) or d.get('version')!=1 or type(d.get('demo')) is not bool or d.get('hedging') is not True:raise ValueError('Only explicitly identified demo/live hedging accounts are supported by this importer')
 if d.get('currency')!='USD' or d.get('server_utc_offset_seconds')!=0:raise ValueError('This importer requires a USD account and UTC+0 MT5 server')
 if 'account_balance' in d:number(d['account_balance'])
 stamp=number(d.get('timestamp'));start=number(d.get('history_from'))
 if not 0<=now-stamp<30 or start>stamp or stamp-start>8*86400:raise ValueError('Trade export is stale or its history window is invalid')
 account=d.get('account_key')
 if not isinstance(account,str) or not 1<=len(account)<=200:raise ValueError('Missing account identity')
 deals=d.get('deals');positions=d.get('positions')
 if not isinstance(deals,list) or not isinstance(positions,list) or len(deals)>100000 or len(positions)>10000:raise ValueError('Invalid export size')
 tickets=set()
 for x in deals:
  ticket=ident(x.get('ticket'));ident(x.get('position_id'))
  if ticket in tickets:raise ValueError('Duplicate deal ticket in export')
  tickets.add(ticket)
  if x.get('side') not in ('buy','sell') or x.get('entry') not in ('in','out','out_by'):raise ValueError('Reversal/netting deals are unsupported; export was not imported')
  symbol=x.get('symbol')
  if not isinstance(symbol,str) or not 1<=len(symbol)<=30 or any(not(ch.isascii() and (ch.isalnum() or ch in '._-')) for ch in symbol):raise ValueError('Invalid symbol')
  if not 0<number(x.get('time'))<=stamp+2:raise ValueError('Invalid deal time')
  for k in ('price','volume'):number(x.get(k),True)
  for k in ('profit','commission','swap','fee'):number(x.get(k))
  for k in ('stop','target'):
   if number(x.get(k,0))<0:raise ValueError('Invalid protective level')
 positions_seen=set()
 for x in positions:
  key=ident(x.get('position_id'))
  if key in positions_seen:raise ValueError('Duplicate open position')
  positions_seen.add(key);number(x.get('volume'),True);number(x.get('floating_pnl'))
  for field in ('stop','target'):
   if field in x and number(x[field])<0:raise ValueError('Invalid position protective level')
 return hashlib.sha256(account.encode()).hexdigest(),stamp,start

def project(deals,positions,coverage_from):
 groups={};out=[];issues=[]
 for d in deals:groups.setdefault(d['position_id'],[]).append(d)
 live={p['position_id']:p for p in positions}
 for pid,items in groups.items():
  qty=0.;avg=0.;cost=0.;opened=None;side=None;symbol=None;invalid=False;rows=[]
  for d in sorted(items,key=lambda x:(x['time'],int(x['ticket']))):
   fees=d['commission']+d['swap']+d['fee'];v=d['volume']
   if d['entry']=='in':
    if qty and (side!=d['side'] or symbol!=d['symbol']):invalid=True;break
    avg=(avg*qty+d['price']*v)/(qty+v);qty+=v;cost+=fees
    opened=d['time'] if opened is None else min(opened,d['time']);side=d['side'];symbol=d['symbol']
   else:
    if qty+1e-8<v or side==d['side'] or symbol!=d['symbol'] or opened is None:invalid=True;break
    allocated=cost*(v/qty);cost-=allocated;qty=max(0,qty-v)
    if d['time']>=coverage_from:
     rows.append(dict(id='mt5-close-'+d['ticket'],source='mt5',position_id=pid,deal_ticket=d['ticket'],symbol=symbol,side=side,lots=v,entry=avg,exit=d['price'],opened_at=opened,closed_at=d['time'],status='closed',pnl=round(d['profit']+fees+allocated,8),gross_profit=d['profit'],commission=d['commission'],swap=d['swap'],fee=d['fee'],allocated_entry_costs=round(allocated,8),strategy='',note='',stop=d.get('stop') or None,target=d.get('target') or None))
  if invalid:issues.append('Position history incomplete or inconsistent: '+pid);continue
  if pid in live:
   if abs(qty-live[pid]['volume'])>1e-7 or opened is None:issues.append('Open volume does not reconcile: '+pid);continue
   rows.append(dict(id='mt5-open-'+pid,source='mt5',position_id=pid,symbol=symbol,side=side,lots=qty,entry=avg,opened_at=opened,status='open',pnl=None,floating_pnl=live[pid]['floating_pnl'],unallocated_entry_costs=round(cost,8),strategy='',note='Entry costs are allocated proportionally as volume closes.'))
  elif qty>1e-7:issues.append('Unreconciled position omitted: '+pid);continue
  out.extend(rows)
 for pid in live.keys()-groups.keys():issues.append('No entry history for open position: '+pid)
 return out,issues

def protection_records(c,trades,data):
 stamp=data['timestamp'];live={p['position_id']:p for p in data['positions']};deals={d['ticket']:d for d in data['deals']}
 for pid,p in live.items():
  values={k:p[k] for k in ('stop','target') if k in p}
  if not values:continue
  previous=c.execute('SELECT payload FROM mt5_journal_protection WHERE position_id=? ORDER BY observed_at DESC LIMIT 1',(pid,)).fetchone()
  if not previous or json.loads(previous[0])!=values:c.execute('INSERT OR REPLACE INTO mt5_journal_protection VALUES(?,?,?)',(pid,stamp,json.dumps(values)))
 for t in trades:
  pid=t['position_id'];cutoff=t.get('closed_at',stamp)
  observations=[(r[0],json.loads(r[1])) for r in c.execute('SELECT observed_at,payload FROM mt5_journal_protection WHERE position_id=? AND observed_at<=? ORDER BY observed_at DESC',(pid,cutoff))]
  last_open={};protection={}
  for field in ('stop','target'):
   observation=next(((at,values[field]) for at,values in observations if field in values),None)
   if observation:last_open[field]={'value':observation[1],'basis':'open-snapshot','observed_at':observation[0]}
   record=live.get(pid,{}) if t['status']=='open' else deals.get(t.get('deal_ticket'),{})
   if field in record:
    protection[field]={'value':record[field],'basis':'open-snapshot' if t['status']=='open' else 'exit-deal','observed_at':stamp if t['status']=='open' else t['closed_at']}
   elif t['status']=='closed' and observation:protection[field]=last_open[field]
   else:protection[field]={'value':None,'basis':'unknown'}
   if t['status']=='open':t[field]=record.get(field) if record.get(field,0)>0 else None
  t['protection']=protection
  if t['status']=='closed' and last_open:t['last_open_protection']=last_open
 return trades

def sync(db_path,export_path,now=None):
 now=time.time() if now is None else now
 with connection(db_path) as c:
  row=c.execute('SELECT payload FROM mt5_journal_meta WHERE id=1').fetchone();previous=json.loads(row[0]) if row else {}
 try:
  raw=Path(export_path).read_bytes()
  if len(raw)>40_000_000:raise ValueError('Trade export too large')
  data=json.loads(raw);account,stamp,start=validate(data,now)
  if previous.get('account') and (previous['account']!=account or previous.get('demo',True)!=data['demo']):raise ValueError('Different MT5 account detected; existing journal was not changed')
  digest=hashlib.sha256(raw).hexdigest()
  if previous.get('hash')==digest:return {**previous,'state':'connected','age_seconds':round(now-stamp,1)}
  with connection(db_path) as c:
   c.execute('BEGIN IMMEDIATE')
   # Recheck account after obtaining the write lock (parallel report requests are safe).
   stored=c.execute('SELECT payload FROM mt5_journal_meta WHERE id=1').fetchone();meta=json.loads(stored[0]) if stored else {}
   if meta.get('account') and (meta['account']!=account or meta.get('demo',True)!=data['demo']):raise ValueError('Different MT5 account detected; journal unchanged')
   if meta.get('timestamp',0)>stamp:return {**meta,'state':'connected','age_seconds':round(now-meta['timestamp'],1)}
   for d in data['deals']:c.execute('INSERT OR REPLACE INTO mt5_journal_deals VALUES(?,?)',(d['ticket'],json.dumps(d)))
   deals=[json.loads(r[0]) for r in c.execute('SELECT payload FROM mt5_journal_deals')]
   coverage=min(meta.get('coverage_from',start),start)
   trades,issues=project(deals,data['positions'],coverage)
   protection_records(c,trades,{**data,'deals':deals})
   # Preserve previously reconciled closed exits on a later partial/incomplete snapshot.
   for t in trades:c.execute('INSERT OR REPLACE INTO mt5_journal_trades VALUES(?,?)',(t['id'],json.dumps(t)))
   active={t['id'] for t in trades if t['status']=='open'}
   for r in c.execute("SELECT id FROM mt5_journal_trades WHERE id LIKE 'mt5-open-%'").fetchall():
    if r[0] not in active:c.execute('DELETE FROM mt5_journal_trades WHERE id=?',(r[0],))
   result=dict(revision=hashlib.sha256(json.dumps([[{k:v for k,v in t.items() if k!='floating_pnl'} for t in trades],issues],sort_keys=True).encode()).hexdigest(),demo=data['demo'],account=account,account_label=account[:8],account_balance=data.get('account_balance'),currency=data['currency'],timestamp=stamp,coverage_from=coverage,hash=digest,deals=len(deals),open_positions=[t for t in trades if t['status']=='open'],closed_count=sum(t['status']=='closed' for t in trades),open_count=len(active),issues=issues,excluded_adjustments=int(data.get('excluded_adjustments',0)),message=('DEMO' if data['demo'] else 'LIVE')+' read-only MT5 deal import. Closed rows are exit fills, including partial closes; entry costs allocated by volume. P/L ledger starts at zero, not account balance. Account-level charges, cash movements and floating P/L excluded.')
   c.execute('INSERT OR REPLACE INTO mt5_journal_meta VALUES(1,?)',(json.dumps(result),))
  return {**result,'state':'connected','age_seconds':round(now-stamp,1)}
 except FileNotFoundError:return {**previous,'state':'waiting','message':'Attach JournalStudioTrades in MT5 on your account (live requires AllowLiveJournal). No trade export received yet.'}
 except (ValueError,TypeError,KeyError,OSError) as exc:return {**previous,'state':'unavailable','message':str(exc) if isinstance(exc,ValueError) else 'Incomplete trade export; retained the last imported journal.'}
