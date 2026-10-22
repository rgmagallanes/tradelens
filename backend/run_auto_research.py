"""Run both preregistered variants/cost scenarios without changing live engine."""
import argparse,hashlib,json
from pathlib import Path
from .history import read_history
from .auto_research import run

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    # Validate a frozen copy to prevent hashing a different timer export.
    raw=args.input.read_bytes();h=read_history(args.input,max_bars=25000)
    if h['state']!='valid':raise SystemExit('Invalid research export')
    if not h['data'].get('demo'):raise SystemExit('Demo history required')
    end=min(max(b['time']+dt for b in h['data']['candles'][tf] if b['closed']) for tf,dt in [('M1',60),('M5',300)] if h['data']['candles'][tf])
    end=end//300*300
    spec=Path(__file__).resolve().parents[1]/'strategy/lower-timeframe-research-v2.md'
    result={'status':'UNPROVEN','source_sha256':hashlib.sha256(raw).hexdigest(),'spec_sha256':hashlib.sha256(spec.read_bytes()).hexdigest(),'clock':'MT5 broker-server','limitations':['Bid OHLC; constant spread/slippage scenarios, not historical executable quotes.','Historical margin, receipt latency and news review unavailable.','Recently viewed data; validation split is not pristine out-of-sample.','Automatic level rules and EMA context differ from approved v1; no live settings changed.'],'runs':[run(h['data'],variant,spread,end=end) for variant in ['reference','lower'] for spread in [6.4,12.8]]}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    for r in result['runs']:print(json.dumps({k:v for k,v in r.items() if k not in ['trades','levels']},indent=2))
if __name__=='__main__':main()
