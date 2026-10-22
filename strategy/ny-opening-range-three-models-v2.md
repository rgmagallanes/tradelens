# New York opening range — three models v2

EXPLORATORY / UNPROVEN. Defined2026-10-21 before running v2 outcomes. Does not replace v1 or activate any engine.

Source: Jdub video bITIVwysCzM. Video concepts:15-minute range, M5 outside close, M1 breakout with gap, retest, failed-break reversal with structure break/displacement and order-block retest. Video examples use2R continuation targets and high-of-day reversal targets. Exact mechanical choices below are ours, not verbatim video rules.

## Shared frozen assumptions
- Same saved BTCUSDm UTC+0 demo bid M1 history and45 complete New York weekday09:30–11:30 sessions as v1;120 exact M1 bars required. No US exchange holiday filter: BTC weekday time anchor only. DST uses America/New_York.
- Range from09:30–09:44, known09:45. Reconstruct post-range M5 closes from M1. A new breakout event is an M5 close outside the range when the previous M5 close was not outside the SAME boundary. A fresh event can follow a close inside or outside the opposite boundary. Consecutive same-side outside closes are one event.
- Candidates generated only from information known by their M1 confirmation close; enter NEXT M1 open, never at the confirmation close. Final signal bar must be before11:29.
- Stop beyond specified candle/zone extreme by0.01. Reject next-open entries with nonpositive initial risk, or reversal targets already behind entry. No sizing/leverage/compounding/partials/trailing/news/volume/EMA/relative-strength filters.
- Stop/target bid touches after entry, including entry minute. Stop gaps at worse open; target gaps at target. Both-touch minute assumes stop first; intraminute ordering unknown. An exit minute blocks all other entries through its end. Time-exit at11:29 close.
- Standalone models and combined strategy each have max3 trades/day, one position at a time. Candidates while a position is open are discarded, never queued for hindsight entry. Same model/side/confirmation-time duplicates are collapsed.
- Combined chronological candidate ordering; identical entry-time conflicts resolved fixed priority breakout, retest, reversal. Report overlapping/day-limit/duplicate skips. Combined results are not sum of standalone results.
- Same two constant spread scenarios6.40/12.80 USD/BTC plus1 USD/BTC slippage per side, zero commission assumed; these are not historical executable quote fills. Short ask-stop triggering, latency/margin/funding unavailable. Report net normalized1BTC exposure and mean netR, not account returns.
- Split first70% complete sessions / last30% chronologically, identical rules. Previously explored history is NOT pristine out-of-sample. No parameter sweep, best-model selection, or profitability guarantee.

## A. Breakout
For each M5 breakout, inspect its final M1 bar and the next4 M1 bars. First directional three-candle wick FVG with a directional middle-candle body and third close outside the range confirms. Bull gap third.low>first.high; bear third.high<first.low. Stop beyond middle candle extreme; fixed2R target. This makes the video's discretionary displacement condition reproducible; no minimum gap size is optimized.

## B. Retest
For each M5 breakout, inspect next30 M1 bars. Bull: wick touches range high, close above it and close>open; bear symmetric. A close through the opposite outer range boundary cancels the event. A brief return inside the broken boundary alone does NOT cancel it (unlike v1). First qualifying retest only per event; stop beyond that retest candle extreme, target2R. The30-minute window, body requirement and far-boundary cancellation are our choices.

## C. Reversal
After an M5 outside break, first subsequent M1 close back at/inside the broken boundary (while still inside opposite boundary) establishes failure. Within next30 M1 bars, seek opposite-side break of the latest confirmed2-left/2-right M1 swing. Pivot needs strict high/low against all4 neighbours; known only after right-hand2 bars close. Pivots must be within this session after the opening range. Require previous close on near side and current close beyond pivot.

Displacement: structure-break candle body exceeds the mean absolute body of the preceding10 M1 bars and is in the reversal direction. This is our numeric proxy; no FVG is mandatory for reversal. Select last opposite-body candle within10 bars before break as order-block proxy, using FULL candle high/low. This zone convention is ours; no claim that it exactly matches the chart drawing in the video.

Within next30 M1 bars, first overlap of zone plus directional body and close beyond zone's far edge confirms. Close through the protective zone edge invalidates. Stop beyond the worse of zone extreme and retest wick. Target the session high-so-far for a long reversal / low-so-far for short, frozen at retest close (no future high/low). Reject target behind next entry. No second retest attempt per parent event.

## Interpretation
This is a bounded three-model Bitcoin adaptation, not an exact replication of discretionary stock selection. Four sources of uncertainty remain separate: small samples, chosen mechanical proxies, previously viewed data, and simplified costs/fills. Preserve losing outputs and original v1; do not silently retune.
