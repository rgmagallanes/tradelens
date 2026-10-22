"""Fixed sizing stress of one disclosed post-hoc candidate, no live writes."""
import argparse,hashlib,json
from pathlib import Path
from .history import read_history
from .high_win_screen import run

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    h=read_history(args.input,max_bars=25000)
    if h['state']!='valid' or not h['data'].get('demo'):raise SystemExit('Valid demo source required')
    data=h['data'];end=min(max(b['time']+dt for b in data['candles'][tf] if b['closed']) for tf,dt in [('M1',60),('M5',300)])//300*300
    root=Path(__file__).resolve().parents[1];files=['strategy/high-risk-sizing-stress-v5.md','strategy/high-win-rate-screen-v4.md','backend/high_win_screen.py']
    result=dict(status='UNPROVEN / MODELED SIZING STRESS',source_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),hashes={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files},candidate='EMA_TREND_RECLAIM',min_net_rr=.5,selection='Post-hoc highest recent-week observed win fraction; no edge established',loss_pause_threshold=20,runs=[])
    for risk in [.005,.01,.02]:
        for spread in [6.4,12.8]:
            for window,start,finish in [('recent_seven_days',end-7*86400,end),('earlier_three_days',end-10*86400,end-7*86400)]:
                r=run(data,'EMA_TREND_RECLAIM',spread,.5,start,finish,risk_fraction=risk,max_risk=1000*risk);r['window']=window;result['runs'].append(r)
                print(json.dumps({k:r.get(k) for k in ['window','risk_fraction','spread','closed_trades','wins','win_rate','net_pnl','realized_drawdown','risk_paused']}),flush=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
