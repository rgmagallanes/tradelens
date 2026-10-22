"""Source-verified, scope-limited scheduled-news experiment. No live writes."""
import argparse,hashlib,json
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
from pathlib import Path
from .history import read_history
from .high_win_screen import run

def calendar_windows(calendar):
    windows=[]
    for e in calendar['events']:
        event=datetime.fromisoformat(e['local_datetime']).replace(tzinfo=ZoneInfo(e['timezone'])).astimezone(timezone.utc)
        windows.append(dict(event_id=e['id'],event_utc=event.isoformat(),start=int((event-timedelta(minutes=e['minutes_before'])).timestamp()),end=int((event+timedelta(minutes=e['minutes_after'])).timestamp()),source=e['source']))
    return windows

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--calendar',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    h=read_history(args.input,max_bars=25000)
    if h['state']!='valid' or not h['data'].get('demo'):raise SystemExit('Valid demo source required')
    data=h['data'];end=min(max(b['time']+dt for b in data['candles'][tf] if b['closed']) for tf,dt in [('M1',60),('M5',300)])//300*300
    calendar=json.loads(args.calendar.read_text());windows=calendar_windows(calendar)
    if int(datetime.fromisoformat(calendar['covered_start_utc']).timestamp())>end-10*86400 or int(datetime.fromisoformat(calendar['covered_end_utc']).timestamp())<end:raise SystemExit('Calendar scope does not cover windows')
    root=Path(__file__).resolve().parents[1]
    evidence=json.loads((root/calendar['offset_evidence']['path']).read_text())
    if evidence.get('server_utc_offset_seconds')!=0:raise SystemExit('Broker clock alignment requires review')
    files=['strategy/scheduled-news-research-v8.md','backend/high_win_screen.py',str(args.calendar),calendar['offset_evidence']['path']]
    out=dict(status='EXPLORATORY / UNPROVEN',source_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),hashes={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files},calendar=calendar,normalized_windows=windows,runs=[])
    for reverse in [False,True]:
        for enabled in [False,True]:
            for spread in [6.4,12.8]:
                for window,start,finish in [('recent_seven_days',end-7*86400,end),('earlier_three_days',end-10*86400,end-7*86400)]:
                    r=run(data,'EMA_TREND_RECLAIM',spread,.5,start,finish,reverse_entries=reverse,news_windows=windows if enabled else None);r['window']=window;r['news_filter']=enabled;out['runs'].append(r)
                    print(json.dumps({k:r.get(k) for k in ['reverse_entries','news_filter','spread','window','closed_trades','wins','net_pnl','risk_paused','skips']}),flush=True)
    args.output.write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
