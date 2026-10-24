#!/usr/bin/env python3
"""Upload validated local demo trades and chart exports. Never sends orders.
Run with --send, optionally --watch; otherwise preview only. No credentials are printed.
"""
import argparse,getpass,json,os,re,sqlite3,time,urllib.request,urllib.error
from pathlib import Path
from urllib.parse import urlsplit
p=argparse.ArgumentParser();p.add_argument('--send',action='store_true');p.add_argument('--prompt-token',action='store_true',help='Read the device token privately from the terminal; never store it.');p.add_argument('--db',type=Path,default=Path(__file__).resolve().parents[2]/'backend/studio.sqlite3');p.add_argument('--watch',action='store_true',help='Upload every 10 seconds until Ctrl+C; token stays in memory.');p.add_argument('--export',type=Path,help='Import this local studio-trades.json before each upload.');p.add_argument('--files-dir',type=Path,default=Path.home()/'Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/users/user/AppData/Roaming/MetaQuotes/Terminal/Common/Files');args=p.parse_args()
def collect():
    with sqlite3.connect(args.db.resolve().as_uri()+'?mode=ro',uri=True) as c:
        row=c.execute('SELECT payload FROM mt5_journal_meta WHERE id=1').fetchone()
        if not row:raise SystemExit('No validated local MT5 journal snapshot. Keep the importer running first.')
        meta=json.loads(row[0]);trades=[json.loads(r[0]) for r in c.execute('SELECT payload FROM mt5_journal_trades')]
    if time.time()-meta.get('timestamp',0)>30:raise SystemExit('Local MT5 snapshot is stale; nothing uploaded.')
    if meta.get('issues'):raise SystemExit('Local importer reports reconciliation issues; nothing uploaded.')
    if meta.get('currency')!='USD':raise SystemExit('Only validated USD demo journals are supported.')
    closed=[t for t in trades if t.get('status')=='closed'];opened=[t for t in trades if t.get('status')=='open']
    payload={'version':1,'demo':True,'currency':'USD','account_hash':meta['account'],'timestamp':int(meta['timestamp']),'trades':closed,'open_positions':opened}
    if meta.get('account_balance') is not None:payload['account_balance']=meta['account_balance']
    print('Validated local export: %d closed rows, %d open positions.'%(len(closed),len(opened)))
    payload['markets']=read_markets(args.files_dir)
    print('Chart exports: %d instrument(s).'%len(payload['markets']))
    return payload

def read_markets(folder):
    result=[]
    for prefix,symbol in [('btc','BTCUSDm'),('xau','XAUUSDm')]:
        try:
            m=json.loads((folder/(prefix+'-studio-candles.json')).read_text())
            if m.get('symbol')!=symbol or m.get('demo') is not True or m.get('server_utc_offset_seconds')!=0:continue
            item={k:m[k] for k in ('symbol','timestamp','demo','terminal_connected','clock','server_utc_offset_seconds')}
            item['candles']={tf:rows[-1000:] for tf,rows in m['candles'].items() if tf in ('M1','M5','M15','H1','H4')}
            try:
                q=json.loads((folder/(prefix+'-studio-quotes.json')).read_text())
                if q.get('symbol')==symbol and q.get('demo') is True:
                    item['quote']={k:q[k] for k in ('version','symbol','timestamp','bid','ask','demo','terminal_connected','quote_age_seconds','tick_time_msc') if k in q}
            except (OSError,ValueError,KeyError):pass
            result.append(item)
        except (OSError,ValueError,KeyError,TypeError):continue
    return result
if args.watch and not args.send:raise SystemExit('--watch requires --send. Preview never uploads.')
if not args.send:
    collect()
    raise SystemExit('Preview only. Nothing sent.')
base=os.environ.get('TRADELENS_UPLOAD_URL','').rstrip('/');secret=os.environ.get('TRADELENS_DEVICE_TOKEN','');u=urlsplit(base)
if u.scheme!='https' or not u.hostname or u.username or u.password or u.query or u.fragment or u.path not in ('','/'):raise SystemExit('Set TRADELENS_UPLOAD_URL to the exact HTTPS site origin.')
if args.prompt_token:
    try:secret=getpass.getpass('Paste your device token (hidden): ').strip()
    except (EOFError,KeyboardInterrupt):raise SystemExit('Cancelled. Nothing uploaded.')
if not secret:raise SystemExit('Configure TRADELENS_DEVICE_TOKEN privately or use --prompt-token.')
while True:
    try:
        if args.export:
            import sys
            sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
            try:import mt5_journal
            except ImportError:from backend import mt5_journal
            state=mt5_journal.sync(args.db,args.export)
            if state.get('state')!='connected' or state.get('issues'):raise ValueError('Local MT5 import is not ready.')
        payload=collect()
        req=urllib.request.Request(base+'/api/device/upload',data=json.dumps(payload,allow_nan=False).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+secret},method='POST')
        with urllib.request.urlopen(req,timeout=30) as response:result=json.load(response)
        print('Upload accepted.' if result.get('accepted') else 'Upload response did not confirm acceptance.',flush=True)
    except urllib.error.HTTPError as e:
        print('Upload rejected (HTTP %d).'%e.code,flush=True)
        if e.code==422:
            try:
                details=json.loads(e.read(16384))
                issues=details.get('issues',[]) if isinstance(details,dict) else []
                for issue in issues[:12]:
                    field=issue.get('field','');code=issue.get('code','')
                    if re.fullmatch(r'[A-Za-z0-9_.]{1,200}',field) and re.fullmatch(r'[a-z_]{1,50}',code):
                        print('Rejected field: '+field+' ('+code+')',flush=True)
                if not issues:print('Server has not supplied field diagnostics. Redeploy the diagnostic update first.',flush=True)
            except (ValueError,TypeError,AttributeError):pass
        if e.code in (401,403,422) or not args.watch:raise SystemExit(1)
    except (OSError,ValueError,sqlite3.Error,SystemExit) as e:
        print('Upload paused: local export is unavailable/stale or host unreachable. Nothing new confirmed.',flush=True)
        if not args.watch:raise SystemExit(1)
    if not args.watch:break
    try:time.sleep(10)
    except KeyboardInterrupt:break
