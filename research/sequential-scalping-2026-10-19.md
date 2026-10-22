# Sequential scalping research v12

**Result: more independent entries, but no profitable edge. Not activated.**

The user selected frequent separate scalps, not stacked positions. This new research candidate keeps exactly one open position, a two-full-M1-candle cooldown after the exit candle, and at most ten entries per Manila day. Entry count is a ceiling, not a trading quota. The original approved live-paper controls and separate H1 research candidate are unchanged.

## Fixed test and results

Data window: 19 August–19 October 2026, 12:00 Exness broker UTC+0, with indicator warmup. M5 EMA trend and M1 EMA9/21 reclaim signals unchanged from v4; this candidate requires at least 1 net R at the original target, enters at the next contiguous M1 open, retains 30-minute exits and planned risk min($5,0.5%equity).

| News filter | Spread/BTC | Closed trades | Wins | Win rate | Modeled P/L | Closed-equity drawdown | Entry-active days |
|---|---:|---:|---:|---:|---:|---:|---:|
| OFF | $6.40 | 84 | 29 | 34.5% | $-99.83 | $101.92 | 18 |
| OFF | $12.80 | 72 | 24 | 33.3% | $-92.90 | $100.84 | 15 |
| ON | $6.40 | 84 | 29 | 34.5% | $-99.83 | $101.92 | 18 |
| ON | $12.80 | 72 | 24 | 33.3% | $-92.90 | $100.84 | 15 |

Normal modeled spread produced 29 wins and 55 losses; average win $5.07 and average loss $4.49, profit factor 0.596. Modeled spread/slippage costs totaled $109.39. The same selected fills with cost addback would have $9.56 accounting P/L, not a valid friction-free policy rerun or proof of a gross edge. More frequent entries increased costs without establishing positive net performance.

## Daily controls and full-period interpretation

A Manila day pauses after three consecutive losses or $20 cumulative negative closes, without offsetting winners. In this research version only, a new Manila date resets those counters and permits a fresh signal; equity is carried continuously. No historical signal is replayed at midnight and no actual live explicit-resume requirement was changed.

The account stops permanently after $100 closed-equity drawdown from its peak. It crossed the threshold on 7 September 04:43 UTC at normal spread and 4 September 05:44 UTC at doubled spread. Thresholds are checked after fills and may overshoot; the normal case reached $101.92 drawdown and closed-equity loss $99.83. It then remained stopped through the rest of the requested window. The full 61-day dataset was observed, not 61 days of active trading.

Maximum entries on any Manila day were 8 at normal spread and 9 at doubled spread, below the cap. News-filter ON per-trade logs exactly matched OFF. All 23 raw scoped-news-window signals per scenario were already risk-paused, so the news filter had no operational entry effect. This does not establish that news avoidance has no value generally.

No open position at data end and no uncertain position crossed a missing-M1 gap in these runs. Input gaps remain present and recorded. Actual spread/slippage, historical margin, latency, news exposure and any overnight funding remain unverified. These are reused-data exploratory results, not prospective validation.

## Verification

63 backend tests passed, including Manila midnight daily reset with carried equity, exact two-full-candle cooldown, daily entry cap, and permanent drawdown stop surviving day changes. A direct trade-log audit verified next-open entries, no overlapping positions, every subsequent entry at least 180 seconds after the prior exit bar opening, risk budgets and the 1 net-R gate. Filter-ON entries are outside scoped blackouts. Old default v4 run-long trade logs reproduce the prior two-month reference at both spreads; new daily behavior is opt-in for this research only. Approved v1 file integrity passed.

## Decision

Retain the desired sequential-scalping style as a product preference, but reject this particular candidate for activation. Do not force ten trades/day, add overlapping positions, widen stops, raise risk or bypass the drawdown stop to recover losses. A different independently justified entry hypothesis and unseen-period evaluation are needed; the H1 candidate remains a separate unproven research result.

Source SHA256: `a3846f5fc2f22a156cfff52f5695c56ebdac0bec5237cabb9e3eb82be238e50e`

`strategy/sequential-scalping-research-v12.md` SHA256: `20b1a95583fb7387a0717e0eca0e47a7502822d4be93f579df239a88ad34562f`

`backend/high_win_screen.py` SHA256: `2a155e9347d1cf6a6f6d4edd7161d5084d46126dd8f9bb1e7e9e1653aab8b0da`

`research/calendars/august-october-2026-core-events.json` SHA256: `a0cd03415e59a628340eeab5198491ac1e7e116aa1e4c4cf758d9c6c872547d2`

Full records and per-day counters: `research/sequential-scalping-2026-10-19.json`. Rules: `strategy/sequential-scalping-research-v12.md`. Decision: `strategy/sequential-scalping-decision-v12.json`. Reproduce via `python -m backend.run_sequential_scalping --input research/exness-history-2months-2026-10-19.json --calendar research/calendars/august-october-2026-core-events.json --output /tmp/sequential-scalping.json`.
