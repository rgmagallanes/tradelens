# Market structure and multi-timeframe execution — source capture

Source: https://www.youtube.com/watch?v=J8NrfzKg4UU
Captured: 2026-10-22. Entire available English caption transcript read (0–880 seconds). Chart visuals have not been independently inspected. This is a source capture, not an executable specification, backtest result, or verified performance claim.

## Framework stated in the video

- 1:57–2:28: Mark relevant levels: previous-day high/low, premarket high/low, or levels from the trader's existing system. Order blocks, supply/demand, imbalances and order flow are examples, not mandatory filters.
- 2:28–4:45: Determine higher-timeframe market structure. Continuation: a break of structure in the trend direction, a resistance/support role flip, and further directional structure. Reversal: a break against the trend through the relevant pivot low/high. Merely losing a nearby level does not establish a full reversal.
- 4:45–6:19: Higher timeframe supplies bias; lower timeframe supplies entry. Explicit scalping pairing: M15 bias and M1 entry. Day-trading example: H1 bias and M15 entry. The presenter also uses M15 and H1 together for context in his examples.
- 6:19–7:00: Use the intermediate timeframe for risk management: M5 between M15 bias and M1 entry. No mechanical trailing-stop algorithm is supplied.

## Demonstrated setups

### AMD: bearish previous-day-low retest (7:09–9:59)

M15 lower highs/lower lows across the preceding two to three days establish bearish context. Mark previous-day high and low. After a break beneath the previous-day low, look for the level to reject as resistance. On M1, upper wicks and an up-close candle provide entry context; M5 also shows an upper wick. Enter short on the rejection, stop above the rejection area, target the known low of day and potential continuation. A fixed 2R target is used for this illustration. Exact order trigger and stop buffer require visual review or explicit research assumptions.

### TSLA: bearish opening-level failure (10:02–12:20)

Bearish M15 context follows weakness over the preceding two sessions. Mark previous-day levels and premarket levels. The presenter discusses three potential shorts: premarket-high rejection, high-of-day rejection followed by a flip back below an opening level, or a break beneath the previous-day low. The demonstrated entry is after high-of-day rejection and a move back below the "opening print," with a stop above that level. Targets are low of day and previous-day low. He later refers to holding beneath the five-minute range low. The precise meaning of "opening print" and its relationship to the plotted range need visual confirmation; do not silently treat it as a specified 15-minute range.

### AAPL: bullish five-minute-range hold (12:23–14:23)

H1 higher highs/higher lows establish bullish context. Mark previous-day high/low. After strength during the first five minutes and a move above previous-day high, consider either a five-minute-range-high break/hold or a previous-day-high retest. On M1, mark the down-close candle and relevant range highs. The demonstrated long follows buyers holding the five-minute range high and the down-close candle. Stop beneath the five-minute range high; illustrated target is 2R. Exact confirmation and stop buffer are not mechanically specified.

## What this does not specify

- No universal first-15-minute opening-range requirement. The AMD example mentions the first 15 minutes descriptively; AAPL and TSLA explicitly refer to five-minute ranges.
- No mandatory FVG, volume threshold, moving-average filter, or institution-position signal.
- No fixed pivot-detection algorithm, candle-close requirement for every break, minimum wick size, level tolerance, expiry, spread cap, maximum daily entries, or account-risk percentage.
- No complete mechanical reversal example; reversal is explained conceptually.
- Examples are US equities. Transfer to Exness BTC, gold, or Nasdaq CFDs needs explicit session definitions, broker data and costs. The video's earnings claims are not independently verified.

## Proposed TradeLens research translation — not yet implemented

Start with two separate continuation candidates: bearish level break/retest and bullish level break/retest. Use M15 bias, M1 confirmation, M5 risk context, premarked levels, and an initially fixed 2R target. Freeze causal pivot rules, completed-bar confirmation, session/day definitions, buffers and costs before testing. Treat five-minute opening-range variants and reversal variants separately. Do not merge this capture into the existing 15-minute ORB results or describe it as proven profitable.
