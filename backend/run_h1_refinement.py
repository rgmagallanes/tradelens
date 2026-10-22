"""Bounded v11 refinement, not an optimizer; all profiles retained."""
import argparse,hashlib,json
from pathlib import Path
from .history import read_history
from .h1_channel_research import run
from .run_two_month_news import START,END


def diagnostics(r):
    trades=r['trades'];net=sum(t['pnl_excluding_swaps'] for t in trades)
    top=max([t['pnl_excluding_swaps'] for t in trades if t['pnl_excluding_swaps']>0]+[0])
    lot_days=sum(t['lots']*(t['hold_hours']+(1 if t['reason'].startswith('STOP') else 0))/24 for t in trades)
    return dict(pnl_without_largest_winner_accounting_only=round(net-top,4),largest_win=top,holding_proxy_lot_days=lot_days,holding_cost_sensitivity_accounting_only=[dict(invented_usd_per_lot_per_24h=rate,cost_proxy=round(lot_days*rate,4),pnl_after_proxy=round(net-lot_days*rate,4)) for rate in [0,10,30]],funding_verified=False)


def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    h=read_history(args.input,max_bars=200000)
    if h['state']!='valid' or not h['data'].get('demo'):raise SystemExit('Valid demo source required')
    root=Path(__file__).resolve().parents[1];files=['strategy/h1-refinement-research-v11.md','strategy/h1-channel-research-v10.md','backend/h1_channel_research.py']
    out=dict(status='EXPLORATORY / UNPROVEN / SWAPS UNVERIFIED',source_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),hashes={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files},runs=[])
    for initial in [1000,10000]:
        for profile in ['baseline','ema50','ema50_range']:
            for spread in [6.4,12.8]:
                r=run(h['data'],START,END,spread=spread,initial=initial,profile=profile)
                if not r['status'].startswith('UNPROVEN'):raise SystemExit(str(r))
                r['diagnostics']=diagnostics(r);out['runs'].append(r)
                print(json.dumps({k:r[k] for k in ['initial_balance','profile','spread','closed_trades','wins','pnl_excluding_swaps','realized_drawdown','risk_paused','skips']}),flush=True)
    args.output.write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
