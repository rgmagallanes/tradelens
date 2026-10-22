"""Copy only the selected read-only MT5 snapshot into the local app."""
import argparse,json,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('source',type=Path);args=p.parse_args()
target=Path(__file__).resolve().parents[1]/'backend'/'mt5-snapshot.json'
while True:
    try:
        data=json.loads(args.source.read_text())
        required=('timestamp','symbol','bid','ask','contract_size','volume_min','volume_step')
        if not all(k in data for k in required): raise ValueError('Missing quote fields')
        temp=target.with_suffix('.tmp');temp.write_text(json.dumps({k:data[k] for k in required}));temp.replace(target)
    except (OSError,ValueError) as e: print(f'Snapshot unavailable: {e}',flush=True)
    time.sleep(2)
