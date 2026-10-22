"""Reproducible v2 breakout versus fixed v3 pullback comparison; no live writes."""
import argparse,hashlib,json
from pathlib import Path
from .history import read_history
from .auto_research import run as breakout
from .pullback_research import run as pullback

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    h=read_history(args.input,max_bars=25000)
    if h['state']!='valid' or not h['data'].get('demo'):raise SystemExit('Valid demo history required')
    data=h['data'];end=min(max(b['time']+dt for b in data['candles'][tf] if b['closed']) for tf,dt in [('M1',60),('M5',300)])//300*300
    root=Path(__file__).resolve().parents[1]
    specs=['strategy/lower-timeframe-research-v2.md','strategy/trend-pullback-research-v3.md']
    result=dict(status='EXPLORATORY / UNPROVEN',clock='MT5 broker-server',source_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),specs={s:hashlib.sha256((root/s).read_bytes()).hexdigest() for s in specs},limitations=['Reused, recently viewed week: both segments are exploratory, not pristine out-of-sample.','Constant modeled spread/slippage and zero commission; historical fills, latency, margin and news review unverified.','Run-long three-loss/$20-negative-loss pause; final segment can remain untraded.'],runs=[])
    for spread in [6.4,12.8]:
        for fn,name in [(breakout,'breakout_retest_v2'),(pullback,'trend_pullback_v3')]:
            run=fn(data,spread=spread,end=end);run['strategy']=name;result['runs'].append(run)
            print(json.dumps({k:v for k,v in run.items() if k not in ('trades','levels','setups')},indent=2),flush=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
