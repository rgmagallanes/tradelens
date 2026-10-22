# H1 channel trend breakout — two-month research v10

**Positive modeled result, still UNPROVEN. All P/L below is after assumed spread/slippage but excludes unverified overnight swaps/funding.**

Period19 August2026 12:00–19 October2026 12:00 Exness broker UTC+0. All1464 expected completed H1 bars present, plus17 August warmup. H1 OHLC drives stop/exit decisions; the51 missing M1 slots do not get used to choose a favorable intrahour path. Tick-level stop gaps/latency remain unknowable.

## Fixed-rule results

| Initial virtual balance | Spread/BTC | Closed trades | Wins | P/L excluding swaps | Closed-equity drawdown | Risk paused |
|---|---:|---:|---:|---:|---:|---|
| $1,000 | $6.40 | 4 | 1 | $+100.46 | $15.76 | 07 Sep 01:00 |
| $1,000 | $12.80 | 4 | 1 | $+100.39 | $15.76 | 07 Sep 01:00 |
| $10,000 | $6.40 | 4 | 1 | $+1,190.04 | $88.36 | 28 Aug 05:00 |
| $10,000 | $12.80 | 4 | 1 | $+1,188.76 | $88.93 | 28 Aug 05:00 |

The$1000 account ended with$1100.46 closed modeled equity at normal spread, before unverified funding. Results come from one large winner followed by three losses, then the rest-of-run pause. Win rate25%, not80%. Modeled spread/slippage costs totaled$0.656 at normal spread and$0.912 at doubled spread. A win fraction or profit factor calculated from four trades is not reliable evidence of future performance.

## Primary$1000 trade log, normal spread

| Direction | Entry, broker time | Exit, broker time | Lots | Exit reason | P/L excluding swaps | Hold |
|---|---|---|---:|---|---:|---:|
| Long | 19 Aug 14:00 | 23 Aug 05:00 | 0.01 | CHANNEL_EXIT | $+116.22 | 87h |
| Long | 30 Aug 13:00 | 30 Aug 21:00 | 0.01 | STOP | $-5.08 | 8h |
| Long | 05 Sep 17:00 | 06 Sep 14:00 | 0.01 | STOP | $-5.25 | 21h |
| Long | 07 Sep 00:00 | 07 Sep 01:00 | 0.01 | STOP | $-5.43 | 1h |

The winner entered19 August14:00 at64962.25 and exited23 August05:00 at76584.04, producing$116.22 on0.01lot. The next three closes lost$5.08,$5.25 and$5.43. Risk budgets grew after the winning trade because this candidate uses0.5% current equity, not an absolute$5 cap. No stop was widened.

The primary account rejected21 signals because a0.01lot position could not fit the planned0.5% loss budget;88 later signals were suppressed by the loss pause. It stopped opening trades7 September, so the full61-day calendar does not mean61days of active trading. The$10000 sensitivity accepted different early trades, held the same initial winner at0.11lot, then paused28 August after three losses. It is not simply ten times the same primary trade list.

## Rules and limits

20-bar completed-close H1 channel breakout, next-H1-open entry; Wilder ATR14 initial stop at2ATR from executable entry; completed-close opposite10-bar channel exit at next opening. No fixed target or30min timeout. One position;0.5% equity planned risk, min/step.01lot; rest-of-run pause at3 consecutive losses or2% initial-equity cumulative negative closes. The$10000 balance is a separately initialized sizing sensitivity, not a recommendation to deposit more money. No news blackout added to these exact proposed H1 rules.

Bid OHLC and constant6.40/12.80 spread, adverse5/BTC/fill slippage, zero modeled commission. Stops use adverse H1 opening price when breached at open. Unknown intrahour gaps may cause worse actual fills. Overnight funding, possible triple swaps and historical margin/leverage availability were not verified and were excluded. Some trades held for multiple days; funding must be established before interpreting profit as executable net return. No end-of-data or uncertain positions in these runs; all16 scenario trade records (four trades repeated across four account/cost scenarios) retained. These are not16 independent market observations. Closed-equity drawdown excludes intratrade unrealized drawdown.

## Verification

56 backend tests passed, including independent ATR seeding/reset cases, channel equality/exclusion, minimum-lot sizing, adverse long/short stop gaps, next-open entry/channel exit timing, open-end exclusion and unknown gaps. An independent raw-data audit of all16 recorded trades rebuilt Wilder ATR, checked prior20 breakout evidence, verified entry prices and stop budgets, checked that no earlier held H1 bar hit the stop, confirmed prior10 exit conditions and recomputed P/L. All audit checks passed. Approved v1 integrity passed; no live settings or paper records were changed.

## Interpretation

This is a more promising observation than the tested scalping variants because one sustained move paid for several small losses. It does not establish a durable edge: the outcome depends on one market trend and only four closes per account, followed by a long pause. The period was already viewed during previous research, and this candidate was selected after those failures. Freeze this version, verify funding and realistic quote execution, then evaluate a separate unseen period and forward demo. Do not retune this positive sample or scale real risk on these four trades.

Source SHA256: `a3846f5fc2f22a156cfff52f5695c56ebdac0bec5237cabb9e3eb82be238e50e`

`strategy/h1-channel-research-v10.md` SHA256: `782cde7f1b286aa99436d4b00e75c22a86025909b3f0d31bce4ab13b475aa3cf`

`backend/h1_channel_research.py` SHA256: `b067c67647a556d610fe1baaa5880a64555d55edc0e2f3511508da403dd9509e`

Specification: `strategy/h1-channel-research-v10.md`. Full results: `research/h1-trend-breakout-2026-10-19.json`. Reproduce via `python -m backend.run_h1_channel --input research/exness-history-2months-2026-10-19.json --output /tmp/h1-channel.json`.
