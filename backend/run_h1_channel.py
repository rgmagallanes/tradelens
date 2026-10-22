"""Run frozen v10 H1 rules; no parameter search and no live writes."""
import argparse,hashlib,json
from pathlib import Path
from .history import read_history
from .h1_channel_research import run
from .run_two_month_news import START,END

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    h=read_history(args.input,max_bars=200000)
    if h['state']!='valid' or not h['data'].get('demo'):raise SystemExit('Valid demo history required')
    bs=[b for b in h['data']['candles']['H1'] if b['closed']];evalbs=[b for b in bs if START<=b['time'] and b['time']+3600<=END]
    root=Path(__file__).resolve().parents[1];files=['strategy/h1-channel-research-v10.md','backend/h1_channel_research.py']
    out=dict(status='EXPLORATORY / UNPROVEN / EXCLUDES UNVERIFIED SWAPS',source_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),hashes={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files},clock='Exness broker UTC+0',start=START,end=END,coverage=dict(completed_h1=len(evalbs),expected_slots=(END-START)//3600,missing_slots=(END-START)//3600-len(evalbs)),runs=[])
    for initial in [1000,10000]:
        for spread in [6.4,12.8]:
            r=run(h['data'],START,END,spread=spread,initial=initial);out['runs'].append(r)
            print(json.dumps({k:v for k,v in r.items() if k!='trades'},indent=2),flush=True)
    args.output.write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
