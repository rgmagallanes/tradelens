"""Fixed directional inversion comparison, isolated from live engine."""
import argparse,hashlib,json
from pathlib import Path
from .history import read_history
from .high_win_screen import run

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    h=read_history(args.input,max_bars=25000)
    if h['state']!='valid' or not h['data'].get('demo'):raise SystemExit('Valid demo source required')
    data=h['data'];end=min(max(b['time']+dt for b in data['candles'][tf] if b['closed']) for tf,dt in [('M1',60),('M5',300)])//300*300
    root=Path(__file__).resolve().parents[1];files=['strategy/reversed-entry-research-v7.md','strategy/high-win-rate-screen-v4.md','backend/high_win_screen.py']
    out=dict(status='EXPLORATORY / UNPROVEN',source_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),hashes={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files},runs=[])
    for reverse in [False,True]:
        for spread in [6.4,12.8]:
            for window,start,finish in [('recent_seven_days',end-7*86400,end),('earlier_three_days',end-10*86400,end-7*86400)]:
                r=run(data,'EMA_TREND_RECLAIM',spread,.5,start,finish,reverse_entries=reverse);r['window']=window;out['runs'].append(r)
                print(json.dumps({k:r.get(k) for k in ['reverse_entries','spread','window','closed_trades','wins','win_rate','net_pnl','realized_drawdown','risk_paused','uncertain_position']}),flush=True)
    args.output.write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
