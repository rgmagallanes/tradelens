# New York opening-range retest — research v1

EXPLORATORY / UNPROVEN. Frozen before the first test on2026-10-21. Separate from the approved engine; no orders or paper-state changes.

Video basis: https://www.youtube.com/watch?v=bITIVwysCzM (English captions retrieved2026-10-21). First15-minute range, M5 outside close, M1 retest, protective structure stop,2R continuation target. This is a Bitcoin adaptation, not the creator's complete discretionary stock method.

## Exact assumptions for this single test
- Input: saved Exness BTCUSDm demo bid OHLC, UTC+0. Use only completed M1 bars, reconstruct M5 from exact contiguous five-minute groups. New York local weekday anchor09:30 using America/New_York (DST-aware); no weekend sessions. This is a BTC weekday anchor, not a US exchange holiday calendar.
- Require all120 one-minute bars from09:30 through11:29 inclusive. Missing/partial sessions skipped completely, reported explicitly.
- Opening range: high/low of09:30–09:44. Cannot act before09:45.
- First completed post-range M5 close strictly above range high establishes long direction; strictly below range low establishes short. Earliest signal09:50. One first breakout only per session.
- From the next M1 bar, allow10 retest bars. Bull retest: low<=range high, close>range high and close>open. Bear is symmetric. A completed close back inside the boundary invalidates the candidate (equality invalidates). Expiration/invalidation ends the day's candidate; no reversal or second entry.
- Enter at next M1 open after retest confirmation, no same-bar entry. Reject if entry has crossed the protective level or next entry bar is beyond the session.
- Stop: bullish retest candle low−0.01; bearish candle high+0.01. Target2× initial bid-reference price risk. Stop/target fixed, no trailing/partials/additional entries/EMA/volume/FVG/news filters. At most one trade per day.
- Exit: later bid-bar stop/target touch, including entry bar after next-open fill. If both touch, assume stop first. Stop gaps fill at worse open; target gaps fill at target, no favourable gap bonus. Time-exit at11:29 close (11:30). No overnight positions.
- Model round-trip costs as spread6.40 or stress12.80 USD/BTC plus1 USD/BTC adverse slippage each side, zero commission assumed for this research scenario. Subtract once from directional bid-reference movement; historical bid/ask/spread are unavailable. Bid touch rules do not simulate real short ask-stop triggering, latency, margin, swap or executable fills.
- Report gross/net price units for normalized1BTC exposure and net R per trade. These are not lot-sized account returns; no leverage, compounding or capital feasibility claims.
- Chronological split: first70% of complete eligible sessions / last30%. Same rules in both. All underlying history was previously explored, so the latter is NOT pristine out-of-sample. No parameter search or choosing the best-cost result.
- Retest timeout, rejection/body rule, one-candidate limit, symmetric shorts, tick buffer and time-exit are our implementation choices, not claims of verbatim video instructions. Outcome summaries must retain these limits.
