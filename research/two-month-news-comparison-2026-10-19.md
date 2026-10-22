# Two-calendar-month scheduled-news experiment v9

**UNPROVEN. No robust profitable result or80% edge demonstrated.**

Period:19 August2026 12:00 to19 October2026 12:00, verified Exness broker UTC+0. Source covers17 August through19 October with warmup. Evaluation has87,789 completed M1 bars of87,840 expected (51 missing minute slots across4 gaps), and17,562 completed M5 bars of17,568 expected (6 missing slots). Gaps are retained in full JSON. All80 scheduled policy/window runs completed.

Primary comparison is a continuous separately initialized$1000 account per policy, preserving the rest-of-run risk pause. Secondary audit uses9 consecutive non-overlapping reset research windows (8 full7-day windows plus final5 days), each reset to$1000. Their sums are descriptive, not the return of one continuously traded account. Those windows are not statistically independent replications.

## Continuous61-day account results

| Direction | Spread/BTC | News OFF P/L | News ON P/L | Trades per policy | Paused at, UTC |
|---|---:|---:|---:|---:|---|
| Original | $6.40 | $-14.19 | $-14.19 | 3 | 19 Aug 13:51 |
| Original | $12.80 | $-13.40 | $-13.40 | 3 | 19 Aug 13:59 |
| Reversed | $6.40 | $-17.86 | $-17.86 | 6 | 19 Aug 16:25 |
| Reversed | $12.80 | $-17.15 | $-17.15 | 6 | 19 Aug 16:25 |

These account runs stopped opening trades after an early risk pause, before the scoped calendar events. Calendar length therefore does not imply61days of active trading. No risk limits were lifted to obtain more trades.

## Descriptive totals across9 reset research windows

| Direction | Spread/BTC | Filter | Wins / trades | Sum of reset-window P/L | Positive windows |
|---|---:|---|---:|---:|---:|
| Original | $6.40 | OFF | 33 / 68 | $-49.98 | 2 /9 |
| Original | $6.40 | ON | 31 / 65 | $-54.52 | 1 /9 |
| Original | $12.80 | OFF | 26 / 63 | $-80.99 | 1 /9 |
| Original | $12.80 | ON | 25 / 61 | $-82.60 | 1 /9 |
| Reversed | $6.40 | OFF | 23 / 59 | $-91.95 | 1 /9 |
| Reversed | $6.40 | ON | 22 / 57 | $-89.85 | 1 /9 |
| Reversed | $12.80 | OFF | 26 / 62 | $-77.91 | 1 /9 |
| Reversed | $12.80 | ON | 25 / 61 | $-80.04 | 1 /9 |

All descriptive grouped sums were negative. News filtering worsened original-direction totals at both spreads. It slightly improved reversed-direction totals at normal spread, but worsened them at doubled spread. None establishes positive expected profit. Some individual windows were positive; they were not selected as a winner and do not establish an edge. All9 windows for every policy reached a risk pause. No run had an uncertain gap position or end-of-window open position.

## Weekly normal-spread detail

| Window | Period, UTC | Original OFF | Original ON | Reversed OFF | Reversed ON |
|---|---|---:|---:|---:|---:|
| 1 | 19 Aug 12:00–26 Aug 12:00 | $-14.19 | $-14.19 | $-17.86 | $-17.86 |
| 2 | 26 Aug 12:00–02 Sep 12:00 | $-9.21 | $-9.21 | $5.33 | $5.33 |
| 3 | 02 Sep 12:00–09 Sep 12:00 | $-5.89 | $-5.89 | $-7.22 | $-7.22 |
| 4 | 09 Sep 12:00–16 Sep 12:00 | $12.79 | $12.79 | $-15.08 | $-15.08 |
| 5 | 16 Sep 12:00–23 Sep 12:00 | $-11.06 | $-11.06 | $-9.54 | $-9.54 |
| 6 | 23 Sep 12:00–30 Sep 12:00 | $-10.14 | $-10.14 | $-13.15 | $-13.15 |
| 7 | 30 Sep 12:00–07 Oct 12:00 | $-4.71 | $-4.71 | $-15.65 | $-15.65 |
| 8 | 07 Oct 12:00–14 Oct 12:00 | $-8.63 | $-8.63 | $-14.50 | $-14.50 |
| 9 | 14 Oct 12:00–19 Oct 12:00 | $1.07 | $-3.48 | $-4.28 | $-2.18 |

The filter changed actual trade logs only in reset window9, which starts14 October12:00 during the CPI blackout. Each filtered policy suppressed4 raw signals there before cost eligibility. A blocked raw signal is not necessarily an otherwise-eligible executable trade. Earlier event windows were largely masked by the rest-of-window loss pauses. This is limited event exposure, not evidence about every news catalyst.

## Calendar scope and fixed rules

Scoped event records: Employment Situation4 September and2 October; CPI11 September and14 October; FOMC statement16 September14:00 Eastern and press conference14:30 Eastern. Data/decision blackout30min before/after; conference30min before to60min after. The overlapping Fed windows cover17:30–19:30 UTC. Sources: [BLS August](https://www.bls.gov/schedule/2026/08_sched.htm), [BLS September](https://www.bls.gov/schedule/2026/09_sched.htm), [BLS October](https://www.bls.gov/schedule/2026/10_sched.htm), [Federal Reserve September calendar](https://www.federalreserve.gov/newsevents/2026-september.htm). America/New_York conversion handles DST. Broker alignment follows Exness documentation and saved zero-offset export. These are scheduled-event facts, not hindsight deletion of losing trades. Calendar collected today is not a fully archived point-in-time database.

Only fixed EMA trend-reclaim v4 and its direction-inverted variant tested; no parameter search. Default0.5%/$5 planned risk, minimum0.5 netR, original ATR target,30-minute exits, one position and fixed$20 cumulative-negative-close/three-loss pause retained. Signal eligibility and sizing are calculated after modeled costs. Targets/stops remain active for positions opened before news; filter does not force flat exposure. No unscheduled news, PPI, speeches, crypto incidents or actual spread-spike filtering tested.

Costs remain modeled: constant$6.40/$12.80 spread perBTC, adverse$5/BTC/fill slippage, zero modeled commission; historical executable quotes, margin, receipt latency and news-review decisions unavailable. Tick-level intra-bar order unknown; stop-first ambiguity handling retained. Dataset extension is additional retrospective evidence, not pristine prospective validation. Closed-equity drawdown excludes unrealized excursions. No policies promoted to live or paper execution.

## Verification

51 backend tests passed, including source-scoped caching equivalence, exact calendar-month span/nonoverlapping reset boundaries, DST/news-window boundaries and preservation of existing-position exits. Research export passed OHLC/chronology/closed-flag validation at full size. All80 runs retained, including unprofitable and paused cases. A direct audit confirms every filter-ON executed entry was outside the declared blackouts. Approved v1 integrity passed; live records unchanged.

Source SHA256: `a3846f5fc2f22a156cfff52f5695c56ebdac0bec5237cabb9e3eb82be238e50e`

`strategy/two-month-news-research-v9.md` SHA256: `c3edf2f4407911e97d3d52551203baf4aba20c13ae5f99fe54529be85a150991`

`backend/high_win_screen.py` SHA256: `506d5209c66871de72fc602c8ea285651341d909a2012b3387f0f43fec634fd4`

`research/calendars/august-october-2026-core-events.json` SHA256: `a0cd03415e59a628340eeab5198491ac1e7e116aa1e4c4cf758d9c6c872547d2`

Raw data: `research/exness-history-2months-2026-10-19.json`. Full80-run output: `research/two-month-news-comparison-2026-10-19.json`. Grouped descriptive audit: `research/two-month-news-summary-2026-10-19.json`. Rules: `strategy/two-month-news-research-v9.md`. Reproduce via `python -m backend.run_two_month_news --input research/exness-history-2months-2026-10-19.json --calendar research/calendars/august-october-2026-core-events.json --output /tmp/two-month-news.json`.
