# High-win-rate scalping screen v4

**Result: no candidate qualified. No 80% winning strategy or positive modeled expectancy was found in this bounded screen.**

Three fixed signal families, two minimum net reward/risk gates (0.5R/1R), two cost scenarios, and two separate initialized windows: 24 runs. No post-result parameter search. These candidate rules are experiments, not implementations of a published guaranteed edge.

Recent window: 12 Oct 12:00–19 Oct 12:00 broker time. Earlier comparison: 9 Oct 12:00–12 Oct 12:00. Historical periods have already been available during research; neither is presented as untouched prospective evidence. All timestamps remain MT5 broker-server clock values.

| Rule | Min net R | Spread/BTC | Window | Wins / closed trades | Win rate | Net P/L | Risk pause |
|---|---:|---:|---|---:|---:|---:|---|
| BB re-entry | 0.5 | $6.40 | Recent 7 days | 0 / 3 | 0.0% | $-13.85 | Yes |
| BB re-entry | 0.5 | $6.40 | Earlier 3 days | 3 / 8 | 37.5% | $-7.28 | Yes |
| BB re-entry | 0.5 | $12.80 | Recent 7 days | 0 / 3 | 0.0% | $-13.31 | Yes |
| BB re-entry | 0.5 | $12.80 | Earlier 3 days | 3 / 8 | 37.5% | $-9.45 | Yes |
| BB re-entry | 1.0 | $6.40 | Recent 7 days | 0 / 3 | 0.0% | $-13.76 | Yes |
| BB re-entry | 1.0 | $6.40 | Earlier 3 days | 2 / 6 | 33.3% | $-5.94 | Yes |
| BB re-entry | 1.0 | $12.80 | Recent 7 days | 0 / 3 | 0.0% | $-13.95 | Yes |
| BB re-entry | 1.0 | $12.80 | Earlier 3 days | 1 / 4 | 25.0% | $-6.81 | Yes |
| Failed-range reversal | 0.5 | $6.40 | Recent 7 days | 1 / 4 | 25.0% | $-11.27 | Yes |
| Failed-range reversal | 0.5 | $6.40 | Earlier 3 days | 0 / 3 | 0.0% | $-13.86 | Yes |
| Failed-range reversal | 0.5 | $12.80 | Recent 7 days | 1 / 4 | 25.0% | $-11.38 | Yes |
| Failed-range reversal | 0.5 | $12.80 | Earlier 3 days | 0 / 3 | 0.0% | $-12.38 | Yes |
| Failed-range reversal | 1.0 | $6.40 | Recent 7 days | 0 / 3 | 0.0% | $-13.55 | Yes |
| Failed-range reversal | 1.0 | $6.40 | Earlier 3 days | 0 / 3 | 0.0% | $-13.86 | Yes |
| Failed-range reversal | 1.0 | $12.80 | Recent 7 days | 0 / 3 | 0.0% | $-14.25 | Yes |
| Failed-range reversal | 1.0 | $12.80 | Earlier 3 days | 0 / 3 | 0.0% | $-12.38 | Yes |
| EMA trend reclaim | 0.5 | $6.40 | Recent 7 days | 4 / 7 | 57.1% | $-1.79 | Yes |
| EMA trend reclaim | 0.5 | $6.40 | Earlier 3 days | 2 / 7 | 28.6% | $-16.86 | Yes |
| EMA trend reclaim | 0.5 | $12.80 | Recent 7 days | 4 / 7 | 57.1% | $-1.99 | Yes |
| EMA trend reclaim | 0.5 | $12.80 | Earlier 3 days | 1 / 5 | 20.0% | $-15.29 | Yes |
| EMA trend reclaim | 1.0 | $6.40 | Recent 7 days | 0 / 3 | 0.0% | $-14.42 | Yes |
| EMA trend reclaim | 1.0 | $6.40 | Earlier 3 days | 1 / 3 | 33.3% | $-2.56 | No |
| EMA trend reclaim | 1.0 | $12.80 | Recent 7 days | 0 / 3 | 0.0% | $-14.42 | Yes |
| EMA trend reclaim | 1.0 | $12.80 | Earlier 3 days | 1 / 3 | 33.3% | $-3.01 | No |

## Interpretation

The largest observed fraction was 4/7 (57.1%), EMA trend reclaim with a 0.5R minimum gate on the recent week. It lost $1.79 at $6.40 spread. Its approximate Wilson95% interval is 25.0%–84.2%, illustrating small-sample uncertainty; serially related trades may make that interval optimistic. This is a post-hoc highest observed fraction, not an independently selected winner.

The same signal/gate won 2 of7 trades and lost $16.86 on the earlier window at normal modeled spread. All24 run totals were negative. Most runs paused after three losses; those pauses censor later opportunities. The screening outcome does not establish that these entire strategy families can never work, but these fixed rules and data do not support the requested80% claim. No candidate reached100 closed trades or positive modeled expectancy.

## Costs and risk

Smaller targets explicitly changed the experimental net-R gate from2R to0.5R/1R; the original approved v1 2R rule is unchanged. Smaller targets can increase winning frequency without improving profitability. No martingale, grid, averaging down, stop widening or hidden loss exclusion. One position, min($5,.5%equity) risk, 30-minute exits, three-loss/$20 cumulative negative realized pause for the rest of each initialized window. All breakeven trades are counted as non-wins.

Bid OHLC with constant modeled $6.40/$12.80 spread and adverse $5/BTC/fill slippage; zero modeled commission. Historical executable quotes, margin, latency and news review are unverified. Stop-first ambiguous candles, adverse gap stops, next-contiguous-M1-open entries and outward stop rounding. Open positions or gaps across positions would be reported/excluded, not assigned favorable fills. No comparison across candidates treats duplicated scenario trades as independent observations.

## Full records and verification

JSON retains all per-trade logs, average win/loss, profit factor, confidence interval, modeled costs, closed-equity drawdown, ambiguity, gaps, risk pause time, suppressed signals and open/uncertain positions. No rule is automatically selected for live or paper activation.

42 backend tests passed. Tests cover prior-only indicator context, chronology at next-open entry, risk pauses, transaction-cost gates and the fact that80% wins can still lose money. Approved v1 frozen-file integrity checked successfully. Existing paper configuration and trading records were not mutated.

Source SHA256: `c94477e213d73f582a1231c5e3771ab0e10ad40dd79c73f4baa01db16d0cd6e3`
Specification SHA256: `f1399c8b666528aa482a0cf9061af088a4e4d701a5f65eeb47c8ea752ce5ebb0`

Specification: `strategy/high-win-rate-screen-v4.md`. Data: `research/exness-history-v2-2026-10-19.json`. Full output: `research/high-win-rate-screen-2026-10-19.json`. Reproduce via `python -m backend.run_high_win_screen --input research/exness-history-v2-2026-10-19.json --output /tmp/high-win-screen.json`.

External context: [CFTC guidance on trading systems and hypothetical performance](https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/fraudadv_tradingsystem.html) explains that simulated performance has limitations and trading systems cannot guarantee profits. This source does not endorse these experimental rules.
