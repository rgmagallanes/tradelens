# Scheduled-news blackout experiment v8

**Result: no performance change; inconclusive about news-filter effectiveness.**

Same fixed EMA trend-reclaim strategy, original and reversed directions, default0.5%/$5 sizing, original targets,0.5 minimum netR, same30-minute hold and run-long loss pause. Filter OFF/ON compared at normal and doubled modeled spreads across separately initialized recent7-day and earlier3-day windows:16 runs. Original v1/live engine records unchanged.

## Calendar and time verification

- [BLS October2026 calendar](https://www.bls.gov/schedule/2026/10_sched.htm): CPI14 October08:30 Eastern, converted with America/New_York to12:30 UTC. Blackout fixed before running:[12:00,13:00) UTC.
- Employment Situation was scheduled2 October, outside the9–19 October tested coverage.
- [Federal Reserve calendar](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm): next October meeting27–28 October, outside coverage. No in-window rate decision/associated press conference.
- [Exness default-timezone documentation](https://get.exness.help/hc/en-us/articles/360014390760-What-is-the-default-timezone-set-for-MetaTrader) states GMT+0. Saved MT5 original snapshot independently records zero server offset. Thus the event conversion is aligned rather than assuming arbitrary broker timestamps are UTC.

Scope is only CPI, Employment Situation and FOMC decisions/press conferences. This is not a complete catalyst calendar. PPI, other releases, speeches, crypto news, exchange incidents and unexpected headlines are excluded. Official calendar consulted today is not a fully archived point-in-time calendar history.

## Paired results

Each cell below is filter OFF = filter ON, net modeled P/L.

| Direction | Spread/BTC | Recent7 days | Earlier3 days |
|---|---:|---:|---:|
| Original | $6.40 | $-1.79 | $-16.86 |
| Original | $12.80 | $-1.99 | $-15.29 |
| Reversed | $6.40 | $-6.86 | $-6.34 |
| Reversed | $12.80 | $-1.48 | $-15.01 |

All actual trade records are identical with the filter enabled versus disabled. It blocked zero otherwise-eligible entries/signals. Each recent-week replay contained four raw event-window signals, but all four were already suppressed by the pre-existing risk pause. The earlier window had no scoped calendar event. These paired scenarios are not independent repetitions and should not be pooled into a larger statistical sample.

This does not prove that avoiding news is ineffective or that news did not affect prices. It shows that the existing run-long risk pause prevented an informative event-window comparison. Do not disable that risk control or delete unfavorable trades after the fact to manufacture a benefit. A longer separate period containing relevant event exposures is needed.

## Filter behavior and limitations

When enabled, block new signals at completed-bar detection time and entries at opening timestamps in blackout. Start is inclusive, end exclusive. Existing positions retain normal stop/target/time exits; a position entered before blackout can remain exposed during an event. The filter does not guarantee a news-flat account. Actual spread spikes, news slippage and unscheduled shocks cannot be verified from constant-spread bid OHLC. Zero commission and fixed adverse slippage remain modeling assumptions; historical margin/latency/news details are unverified. Reused historical data and prior candidate selection mean no clean out-of-sample claim.

## Verification

49 backend tests passed, including Eastern DST conversion, exact blackout boundaries, suppression at detection, allowed re-entry at blackout end, and an existing position retaining its target exit during blackout. Filter-OFF per-trade logs reproduce all8 v7 original scenarios. Filter-ON logs exactly match corresponding OFF logs on this dataset. Approved v1 integrity check passed. No automatic calendar filter was activated in the live app.

Risk pause timestamps:
- original, spread$6.40, recent_seven_days: 2026-10-12 15:00 broker time.
- original, spread$6.40, earlier_three_days: 2026-10-09 15:21 broker time.
- original, spread$12.80, recent_seven_days: 2026-10-12 17:37 broker time.
- original, spread$12.80, earlier_three_days: 2026-10-09 15:21 broker time.
- reversed, spread$6.40, recent_seven_days: 2026-10-12 17:38 broker time.
- reversed, spread$6.40, earlier_three_days: 2026-10-09 18:15 broker time.
- reversed, spread$12.80, recent_seven_days: 2026-10-12 22:28 broker time.
- reversed, spread$12.80, earlier_three_days: 2026-10-11 16:28 broker time.

Source SHA256: `c94477e213d73f582a1231c5e3771ab0e10ad40dd79c73f4baa01db16d0cd6e3`

`strategy/scheduled-news-research-v8.md` SHA256: `dc9e1232e651ee3a86c4b2e97e5549ad38f464a662f319d365204233f30aaa06`

`backend/high_win_screen.py` SHA256: `424a901f660741a47e885dce820bd095c16ba772507f19337c2037396a28e950`

`research/calendars/october-2026-core-events.json` SHA256: `42815b42bd33a65534489c762982fbeb72599ddb9d0ffdab0d53d4aea660a604`

`research/exness-candles-2026-10-19.json` SHA256: `0d2f4889b49c9cd85d4db176e860d165b80d3e8c37b3b2d10deed56a2b8ed28d`

Full results: `research/scheduled-news-comparison-2026-10-19.json`. Normalized calendar: `research/calendars/october-2026-core-events.json`. Rules: `strategy/scheduled-news-research-v8.md`. Reproduce using `python -m backend.run_news_comparison --input research/exness-history-v2-2026-10-19.json --calendar research/calendars/october-2026-core-events.json --output /tmp/news-comparison.json`.
