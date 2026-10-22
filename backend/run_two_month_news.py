"""Fixed two-calendar-month comparison plus explicitly reset weekly audit."""
import argparse,hashlib,json
from pathlib import Path
from datetime import datetime
from .history import read_history
from .run_news_comparison import calendar_windows
from .high_win_screen import run
START=1787140800 # 2026-08-19 12:00 UTC
END=1792411200   # 2026-10-19 12:00 UTC

def run_windows(start=START,end=END):
    windows=[('continuous_two_months',start,end)]
    a=start;i=1
    while a<end:
        b=min(a+7*86400,end);windows.append((f'reset_week_{i}',a,b));a=b;i+=1
    return windows

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--calendar',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    h=read_history(args.input,max_bars=200000)
    if h['state']!='valid' or not h['data'].get('demo'):raise SystemExit('Valid demo source required')
    data=h['data'];cal=json.loads(args.calendar.read_text());news=calendar_windows(cal)
    coverage={}
    for tf,dt in [('M1',60),('M5',300)]:
        bs=[b for b in data['candles'][tf] if b['closed']]
        if not bs or bs[0]['time']>START-(60*dt if tf=='M5' else 21*dt) or bs[-1]['time']+dt<END:raise SystemExit('Incomplete '+tf+' coverage; no two-month result produced')
        use=[b for b in bs if START<=b['time'] and b['time']+dt<=END]
        coverage[tf]=dict(first=bs[0]['time'],last=bs[-1]['time'],evaluation_bars=len(use),expected_slots=(END-START)//dt,missing_slots=(END-START)//dt-len(use),gaps=[dict(after=a['time'],before=b['time']) for a,b in zip(use,use[1:]) if b['time']-a['time']!=dt])
    if int(datetime.fromisoformat(cal['covered_start_utc']).timestamp())>START or int(datetime.fromisoformat(cal['covered_end_utc']).timestamp())<END:raise SystemExit('Insufficient calendar scope')
    root=Path(__file__).resolve().parents[1]
    clock=json.loads((root/cal['offset_evidence']['path']).read_text())
    if clock.get('server_utc_offset_seconds')!=0 or abs(data.get('server_utc_offset_seconds',0))>2:raise SystemExit('Broker clock alignment requires review')
    files=['strategy/two-month-news-research-v9.md','backend/high_win_screen.py',str(args.calendar)]
    out=dict(status='EXPLORATORY / UNPROVEN',start=START,end=END,source_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),hashes={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files},coverage=coverage,calendar=cal,normalized_windows=news,runs=[])
    cache={} # Raw signals depend only on this fixed source, not policy or research window.
    for window,start,end in run_windows():
        for reverse in [False,True]:
            for enabled in [False,True]:
                for spread in [6.4,12.8]:
                    r=run(data,'EMA_TREND_RECLAIM',spread,.5,start,end,reverse_entries=reverse,news_windows=news if enabled else None,signal_cache=cache);r.update(window=window,news_filter=enabled);out['runs'].append(r)
                    print(json.dumps({k:r.get(k) for k in ['window','reverse_entries','news_filter','spread','closed_trades','net_pnl','risk_paused','uncertain_position']}),flush=True)
        args.output.write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
