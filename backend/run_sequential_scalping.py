"""Fixed v12 daily-managed sequential scalping research; no live writes."""
import argparse,hashlib,json
from pathlib import Path
from .history import read_history
from .high_win_screen import run
from .run_news_comparison import calendar_windows
from .run_two_month_news import START,END

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--calendar',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    h=read_history(args.input,max_bars=200000)
    if h['state']!='valid' or not h['data'].get('demo'):raise SystemExit('Valid demo source required')
    cal=json.loads(args.calendar.read_text());news=calendar_windows(cal)
    root=Path(__file__).resolve().parents[1];files=['strategy/sequential-scalping-research-v12.md','backend/high_win_screen.py',str(args.calendar)]
    out=dict(status='EXPLORATORY / UNPROVEN',source_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),hashes={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files},runs=[]);cache={}
    for enabled in [False,True]:
        for spread in [6.4,12.8]:
            r=run(h['data'],'EMA_TREND_RECLAIM',spread,1.,START,END,news_windows=news if enabled else None,signal_cache=cache,daily_reset=True,cooldown_seconds=120,max_daily_entries=10,drawdown_limit=100)
            r['news_filter']=enabled;out['runs'].append(r)
            print(json.dumps({k:r.get(k) for k in ['news_filter','spread','closed_trades','wins','win_rate','net_pnl','modeled_costs','realized_drawdown','processed_end','permanent_pause','open_position','uncertain_position','skips']},indent=2),flush=True)
    args.output.write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
