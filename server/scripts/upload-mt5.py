#!/usr/bin/env python3
"""Explicit one-shot upload of already validated local demo trades. Never sends orders.
Run manually with --send; otherwise prints counts only. No credentials are printed.
"""
import argparse,json,os,sqlite3,time,urllib.request,urllib.error
from pathlib import Path
from urllib.parse import urlsplit
p=argparse.ArgumentParser();p.add_argument('--send',action='store_true');p.add_argument('--db',type=Path,default=Path(__file__).resolve().parents[2]/'backend/studio.sqlite3');args=p.parse_args()
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
if not args.send:raise SystemExit('Preview only. Nothing sent. Use --send after configuring your private uploader environment.')
base=os.environ.get('TRADELENS_UPLOAD_URL','').rstrip('/');secret=os.environ.get('TRADELENS_DEVICE_TOKEN','');u=urlsplit(base)
if u.scheme!='https' or not u.hostname or u.username or u.password or u.query or u.fragment or u.path not in ('','/'):raise SystemExit('Set TRADELENS_UPLOAD_URL to the exact HTTPS site origin.')
if not secret:raise SystemExit('Configure TRADELENS_DEVICE_TOKEN privately.')
req=urllib.request.Request(base+'/api/device/upload',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+secret},method='POST')
try:
    with urllib.request.urlopen(req,timeout=30) as response:result=json.load(response)
    print('Upload accepted.' if result.get('accepted') else 'Upload response did not confirm acceptance.')
except urllib.error.HTTPError as e:raise SystemExit('Upload rejected (HTTP %d). Check token, account pin and export freshness.'%e.code)
except (urllib.error.URLError,TimeoutError):raise SystemExit('Upload could not reach the hosted journal. No retry performed.')
