# Three opening-range models — Bitcoin research v2

**EXPLORATORY / UNPROVEN. Not ready for activation.**

45 complete weekday New York09:30–11:30 sessions,17August–16October2026.19October was incomplete (61 missing M1 bars) and skipped. This is a BTCUSDm Exness demo bid-OHLC adaptation, not an exact replication of discretionary stock selection. Gold was not tested.

Rules were written before v2 outcomes in [the v2 specification](../strategy/ny-opening-range-three-models-v2.md). No parameters were selected from a sweep. Original v1 files remain intact. No live/paper settings changed.

## All models and cost scenarios

| Model | Trades | Win rate normal cost | Gross | Net normal cost | Net stress cost | PF normal |
|---|---:|---:|---:|---:|---:|---:|
|Breakout|52|30.8%|-1244.35|-1681.15|-2013.95|0.737|
|Retest|46|39.1%|+391.46|+5.06|-289.34|1.002|
|Reversal|15|33.3%|+288.91|+162.91|+66.91|1.130|
|Combined|86|34.9%|+169.78|-552.62|-1103.02|0.936|

All movement and net amounts are normalized USD price movement for1BTC exposure per trade, **not account returns or suggested size**. Normal cost:6.40 spread +1 slippage each side =8.40 round trip. Stress:12.80 spread +1 each side =14.80. No leverage, position sizing, capital/margin feasibility, compounding, historical executable bid/ask, funding or receipt latency is modeled.

## Chronological stability check

First31 complete sessions / final14 from29September. Previously explored underlying history; the later segment is NOT pristine out-of-sample.

| Model | Early trades | Early net | Later trades | Later net |
|---|---:|---:|---:|---:|
|Breakout|35|-1288.31|17|-392.84|
|Retest|32|+816.58|14|-811.52|
|Reversal|12|+396.32|3|-233.41|
|Combined|59|+363.13|27|-915.75|

Every model lost in the later segment. Retest overall+5.06 (PF1.002) is effectively flat and turns negative under higher costs. Reversal overall+162.91 uses only15 trades, falls to+66.91 stressed, and has negative mean netR (−0.008 normal /−0.062 stress). Variable risk distances weight fixed-exposure P/L differently from equal-risk R averages; this is not a validated sizing system or demonstrated edge. Combined gross+169.78 became net−552.62 after722.40 modeled costs.

## Why trade counts increased

- New M5 outside breaks can rearm after an intervening inside/opposite close. Consecutive same-side outside closes remain one event.
- Retest now allows30 minutes and brief closes inside the broken boundary; only the opposite range boundary cancels it. These are explicit v2 assumptions, not parameter optimizations or direct video quotations.
- Three distinct models generated120 unique candidates:53 breakout,51 retest and16 reversal.
- Standalone execution accepted52/46/15 trades, respectively. Each standalone has its own independent one-position and3-trade/day constraints; they cannot be added to form a combined portfolio.
- Combined priority breakout→retest→reversal for simultaneous signals, one open position, max3/day:86 accepted;22 overlap and12 day-limit candidates skipped. Every signal is used causally or discarded, never queued for a later hindsight entry.

## Model limits

- Breakout: directional M1 wick FVG, formed at/within4 minutes after M5 confirmation; middle candle directional; stop beyond middle candle;2R target.
- Retest: directional M1 body/close after boundary touch, next-open entry; stop beyond retest candle;2R target.
- Reversal: failed M5 break, causally confirmed2-left/2-right pivot, opposite structure break with body larger than preceding10-bar mean, last opposing candle full-range zone, subsequent zone retest, known high/low-of-day target. These pivot/displacement/zone conventions mechanically approximate discretionary concepts.
- No reversal EMA/volume/FVG mandate, no relative-strength stock selection, and no news filter. No claim that all chart examples would be captured.
- Stop-first if both barriers touched in one minute;0 actual ambiguous trades in this run. Stops gap to worse open and targets receive no gap bonus. Short ask-stop triggering remains unmodeled.

## Verification and artifacts

-11 focused tests passed across v1/v2, including synthetic long/short reversals, confirmed-pivot timing, future-price invariance, next-open entries, overlap/day caps, stop-gap/both-touch behavior, costs and DST.
- Independent auditor checked398 trade-scenario rows across8 scenarios: source/spec hashes, timing, OR levels, model evidence, frozen reversal targets, reconstructed exits, cost/netR accounting and nonoverlap/caps.
- [Detailed results and all candidate/trade records](ny-opening-range-three-models-v2-2026-10-21.json)
- [Independent audit](ny-opening-range-three-models-v2-audit-2026-10-21.json)

The next useful step is visual setup review or genuinely new forward data, not increasing leverage or repeatedly modifying this sample until it turns profitable.
