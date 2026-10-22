# High-risk sizing stress v5

**UNPROVEN. Larger sizing did not establish an improved trading edge. No live changes.**

Fixed EMA trend-reclaim v4, 0.5 minimum net-R gate, bid OHLC and the same saved source snapshot. Initial modeled equity1000. Each window resets independently. Dollar caps $5/$10/$20 accompany0.5%/1%/2% equity risk. All other signal and fill rules remain fixed, as do the $20 cumulative negative-realized-loss and three-loss pauses. Selected candidate had the highest observed v4 recent-week win fraction, so selection bias remains.

| Risk/trade | Spread/BTC | Window | Wins / trades | Net modeled P/L | Closed-equity drawdown | Paused |
|---|---:|---|---:|---:|---:|---|
| 0.5% | $6.40 | Recent 7 days | 4 / 7 | $-1.79 | $14.23 | Yes |
| 0.5% | $6.40 | Earlier 3 days | 2 / 7 | $-16.86 | $19.51 | Yes |
| 0.5% | $12.80 | Recent 7 days | 4 / 7 | $-1.99 | $14.43 | Yes |
| 0.5% | $12.80 | Earlier 3 days | 1 / 5 | $-15.29 | $15.29 | Yes |
| 1.0% | $6.40 | Recent 7 days | 4 / 7 | $-2.10 | $28.46 | Yes |
| 1.0% | $6.40 | Earlier 3 days | 2 / 5 | $-16.81 | $22.11 | Yes |
| 1.0% | $12.80 | Recent 7 days | 4 / 7 | $-2.91 | $29.27 | Yes |
| 1.0% | $12.80 | Earlier 3 days | 1 / 4 | $-22.93 | $22.93 | Yes |
| 2.0% | $6.40 | Recent 7 days | 4 / 6 | $14.37 | $38.36 | Yes |
| 2.0% | $6.40 | Earlier 3 days | 1 / 3 | $-28.02 | $39.15 | Yes |
| 2.0% | $12.80 | Recent 7 days | 4 / 6 | $13.62 | $39.11 | Yes |
| 2.0% | $12.80 | Earlier 3 days | 1 / 3 | $-26.67 | $26.67 | Yes |

## Why the recent 2% run was positive

At normal modeled spread, its first six entries/directions/stops/targets are exactly the same as the first six trades of the 0.5% run. Larger sizing crossed the unchanged negative-loss pause threshold sooner, so the 2% run did not take the seventh losing trade. Thus the 4/6 (66.7%) fraction versus4/7 (57.1%) is a different stopped sample, not evidence that sizing predicted better entries. The recent2% run realized $14.37 profit but fell $38.36 from its closed-equity peak; the earlier2% run lost $28.02 with $39.15 realized drawdown. Doubled modeled spread retained recent profit $13.62 but earlier loss $26.67. Do not pool the reset windows into one continuously traded account or present one favorable window as validation.

The $20 threshold is checked after a close and sums negative trades without offsetting winners. It is not a maximum-loss guarantee. The recent2% run accumulated about$38.36 in negative closes before pausing, despite positive overall net P/L. Risk/drawdown figures here exclude unrealized intratrade excursions and unobserved quote gaps.

## Limitations

Constant modeled spread/slippage, zero modeled commission; historical margin, executable bid/ask, latency and news unverified. Larger lot sizes may not be executable given historical margin. Same previously viewed data, not fresh validation. No candidate has shown a reliable80% future win probability. No automatic promotion, live-risk increase, leverage change or broker orders. Neither favorable sizing nor historical pause timing is proof of an edge.

## Verification

43 backend tests passed. The0.5% results reproduce the prior saved screen for every cost/window combination. Direct trade-log comparison verified identical first-six trade prices in the recent0.5% and2% runs; only sizes and later pause eligibility differ. Approved v1 integrity check passed.

Source SHA256: `c94477e213d73f582a1231c5e3771ab0e10ad40dd79c73f4baa01db16d0cd6e3`

`strategy/high-risk-sizing-stress-v5.md` SHA256: `ca930bcf739f720be3e782fd042c04ad4edaed2b74eefd05cb0e850c6fe83fd5`

`strategy/high-win-rate-screen-v4.md` SHA256: `f1399c8b666528aa482a0cf9061af088a4e4d701a5f65eeb47c8ea752ce5ebb0`

`backend/high_win_screen.py` SHA256: `4624a95ab7d92f4a12b3e22d865d2cbe8c193dcbc63a6afae1383e97745eca9a`

Full result: `research/high-risk-stress-2026-10-19.json`. Specification: `strategy/high-risk-sizing-stress-v5.md`. Reproduce with `python -m backend.run_risk_stress --input research/exness-history-v2-2026-10-19.json --output /tmp/risk-stress.json`.
