"""Execute all fixed v4 candidates/windows; retain every result, no best-rule selection."""
import argparse,hashlib,json
from pathlib import Path
from .history import read_history
from .high_win_screen import FAMILIES,run

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    h=read_history(args.input,max_bars=25000)
    if h['state']!='valid' or not h['data'].get('demo'):raise SystemExit('Valid demo history required')
    data=h['data'];end=min(max(b['time']+dt for b in data['candles'][tf] if b['closed']) for tf,dt in [('M1',60),('M5',300)])//300*300
    spec=Path(__file__).resolve().parents[1]/'strategy/high-win-rate-screen-v4.md'
    results=[]
    for family in FAMILIES:
        for rr in [.5,1.]:
            for spread in [6.4,12.8]:
                for window,start,finish in [('recent_seven_days',end-7*86400,end),('earlier_three_days',end-10*86400,end-7*86400)]:
                    r=run(data,family,spread,rr,start,finish);r['window']=window;results.append(r)
                    print(json.dumps({k:r.get(k) for k in ['family','window','spread','min_net_rr','closed_trades','wins','win_rate','net_pnl','risk_paused','research_flag','uncertain_position'] if k!='trades'}),flush=True)
    qualified=[]
    for family in FAMILIES:
        for rr in [.5,1.]:
            group=[r for r in results if r['family']==family and r.get('min_net_rr')==rr]
            if len(group)==4 and all(r.get('research_flag') for r in group):qualified.append(dict(family=family,min_net_rr=rr))
    out=dict(status='EXPLORATORY / UNPROVEN',clock='MT5 broker-server',spec_sha256=hashlib.sha256(spec.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),candidate_count=6,cost_scenarios=2,windows=2,qualified_for_further_research=qualified,limitations=['No future 80% probability established.','Reused historical data and multiple candidates: selection bias remains; no automatic rule selection.','Candle-based modeled constant spread and slippage; historical executable quotes, margin, latency and news unverified.','Wilson interval is an independence approximation; trade clustering can widen uncertainty.','Research uses .5R/1R gates without changing approved-v1 2R or live settings.'],runs=results)
    args.output.write_text(json.dumps(out,indent=2)+'\n')
    print('QUALIFIED',qualified)
if __name__=='__main__':main()
