"""Fixed v13 comparison. Requires real exported tick counts; no live writes."""
import argparse,hashlib,json
from pathlib import Path
from .history import read_history
from .high_win_screen import run
from .run_news_comparison import calendar_windows
from .run_two_month_news import START,END

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def parity(original,current):
    counts={}
    for tf in ['M1','M5']:
        old={b['time']:b for b in original['candles'][tf] if b['closed'] and START-18000<=b['time']<END}
        new={b['time']:b for b in current['candles'][tf] if b['closed'] and START-18000<=b['time']<END}
        if old.keys()!=new.keys():raise ValueError(tf+' history timestamps changed')
        if any(any(old[t][k]!=new[t][k] for k in ['open','high','low','close']) for t in old):raise ValueError(tf+' historical prices changed')
        counts[tf]=len(old)
    return counts

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--original',type=Path,default=Path('research/exness-history-2months-2026-10-19.json'));p.add_argument('--calendar',type=Path,default=Path('research/calendars/august-october-2026-core-events.json'));p.add_argument('--output',type=Path,default=Path('research/volume-scalping-2026-10-19.json'));args=p.parse_args()
    out=dict(status='BLOCKED',runs=[],source_path=str(args.input))
    try:
        h=read_history(args.input,max_bars=200000);old=read_history(args.original,max_bars=200000)
        if h['state']!='valid' or old['state']!='valid':raise ValueError('Waiting for valid volume history export')
        if not h['data'].get('demo') or not h['data'].get('terminal_connected'):raise ValueError('Connected demo export required')
        out.update(source_sha256=digest(args.input),original_sha256=digest(args.original),parity=parity(old['data'],h['data']))
        bars=[b for b in h['data']['candles']['M1'] if b['closed'] and START-1200<=b['time']<END]
        if any(type(b.get('tick_volume')) is not int or b['tick_volume']<0 for b in bars) or not any(b.get('tick_volume',0)>0 for b in bars):raise ValueError('Missing or invalid historical tick volume')
        out['volume_audit']=dict(bars=len(bars),zero_tick_bars=sum(b['tick_volume']==0 for b in bars),nonzero_real_volume_bars=sum(b.get('real_volume',0)>0 for b in bars))
        out['hashes']={str(f):digest(f) for f in [Path('strategy/volume-scalping-research-v13.md'),Path('backend/high_win_screen.py'),Path(__file__),args.calendar]}
        news=calendar_windows(json.loads(args.calendar.read_text()));cache={}
        for enabled in [False,True]:
            for spread in [6.4,12.8]:
                for threshold in [None,1.5]:
                    r=run(h['data'],'EMA_TREND_RECLAIM',spread,1.,START,END,news_windows=news if enabled else None,signal_cache=cache,daily_reset=True,cooldown_seconds=120,max_daily_entries=10,drawdown_limit=100,volume_multiplier=threshold)
                    r['news_filter']=enabled;out['runs'].append(r)
                    print(json.dumps({k:r.get(k) for k in ['volume_multiplier','news_filter','spread','closed_trades','win_rate','net_pnl','realized_drawdown','status']}),flush=True)
        out['status']='EXPLORATORY / UNPROVEN'
    except (ValueError,OSError) as e:out['reason']=str(e)
    args.output.write_text(json.dumps(out,indent=2)+'\n')
    lines=['# Tick-volume scalping comparison','',out['status'],'']
    if out.get('reason'):lines.append(out['reason'])
    else:
        lines+=['| Volume filter | News | Spread | Trades | Win rate | Net P/L | Closed-equity DD |','|---|---|---|---:|---:|---:|---:|']
        for r in out['runs']:
            wr=f"{r['win_rate']:.1%}" if r['win_rate'] is not None else 'N/A'
            lines.append(f"| {r['volume_multiplier'] or 'Off'} | {r['news_filter']} | {r['spread']} | {r['closed_trades']} | {wr} | ${r['net_pnl']:.2f} | ${r['realized_drawdown']:.2f} |")
    lines+=['','Research only. Tick volume measures quote activity, not institutional identities. Previously viewed data; costs are modeled and funding/margin unverified. No live activation. See JSON for source hashes, parity audit and complete trade/risk records.']
    args.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')
    if out['status']=='BLOCKED':print(out['reason'])
if __name__=='__main__':main()
