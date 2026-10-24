#!/usr/bin/env python3
"""Import her own local MT5 demo/live export; upload only with explicit --send."""
import argparse,os,subprocess,sys
from pathlib import Path
import mt5_journal
p=argparse.ArgumentParser(description='TradeLens Mac journal setup. Default is a local preview; nothing sent.')
p.add_argument('--allow-live',action='store_true',help='Explicit read-only live journaling opt-in; live chart feeds excluded.')
p.add_argument('--send',action='store_true',help='Upload to https://tradelens.chardee.dev after a hidden device-token prompt.')
p.add_argument('--export',type=Path,help='Exact path to MT5 Common/Files/studio-trades.json if auto-discovery is unavailable.')
p.add_argument('--cache-dir',type=Path,default=Path.home()/'Library/Application Support/TradeLensUploader')
p.add_argument('--watch',action='store_true',help='Keep syncing every 10 seconds; use with --send.');args=p.parse_args();os.umask(0o077)
if args.export:
    export=args.export.expanduser().resolve()
else:
    support=Path.home()/'Library/Application Support'
    candidates=list(support.glob('*/drive_c/users/*/AppData/Roaming/MetaQuotes/Terminal/Common/Files/studio-trades.json'))
    candidates+=list((Path.home()/'.wine').glob('drive_c/users/*/AppData/Roaming/MetaQuotes/Terminal/Common/Files/studio-trades.json'))
    candidates=list(dict.fromkeys(p.resolve() for p in candidates))
    if len(candidates)!=1:raise SystemExit('Could not identify one MT5 export. Attach JournalStudioTrades on one chart, then use --export with the exact studio-trades.json file path if needed.')
    export=candidates[0]
if args.allow_live:args.cache_dir=args.cache_dir/'live'
args.cache_dir.mkdir(parents=True,exist_ok=True,mode=0o700)
db=args.cache_dir/'journal.sqlite3';result=mt5_journal.sync(db,export)
if result.get('state')!='connected' or result.get('issues'):raise SystemExit('Local import not ready: '+result.get('message','Reconciliation required. Nothing sent.'))
if result.get('demo',True) is False and not args.allow_live:raise SystemExit('LIVE account detected. Run again with --allow-live for read-only live journaling.')
command=[sys.executable,str(Path(__file__).with_name('upload-mt5.py')),'--db',str(db),'--files-dir',str(export.parent),'--export',str(export)]
if args.allow_live:command+=['--allow-live']
env=os.environ.copy();env.pop('TRADELENS_DEVICE_TOKEN',None);env['TRADELENS_UPLOAD_URL']='https://tradelens.chardee.dev'
if args.send:
    print('Destination: https://tradelens.chardee.dev — your trade history, current open positions and balance metadata plus demo-only Bitcoin/Gold candles and quotes will be uploaded under the device token you enter.',flush=True)
    command+=['--send','--prompt-token']
    if args.watch:command+=['--watch']
result=subprocess.run(command,env=env)
# Preserve failures; no automatic retries or uploads.
raise SystemExit(result.returncode)
