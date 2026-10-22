# BTC Studio — breakout/retest v1 proposal

Status: APPROVED BASELINE v1 · UNPROVEN · paper research only
Date: 2026-10-19 (Asia/Manila)
Instrument: Exness demo BTCUSDm
Approved by the user on 2026-10-19 for automatic paper-engine implementation and testing. Broker order execution remains unauthorized.

## What this specification establishes

One reproducible candidate for testing. It is not a profitability claim. The video supplies the four-part framework (map, confirmation, invalidation, context). All numeric thresholds, lower timeframes, context filter, entry mechanics, targets, time limits and risk limits below are OUR research assumptions. They are not attributed to the creator.

The current app has live demo quotes/candles, manual controls and a synthetic paper trader. It does NOT implement this specification. User approval authorizes implementing and testing the paper engine, not live orders.

## 1. Data and chronology

- H1: directional context. M15: manually registered support/resistance. M5: breakout and retest confirmation. M1: collect only; never used for entry, exits, filtering or resolving ambiguous M5 histories in v1.
- Price-action conditions use broker candle OHLC, with the price basis recorded. Before testing, verify whether BTCUSDm chart candles represent bid or another basis. Do not silently treat bid candles as ask candles.
- Only completed candles qualify. A newer bar must establish that the previous M5 bar is closed. The currently forming candle cannot confirm anything.
- Evaluate an event only after its data have actually arrived. Store broker bar time, local receipt UTC time, source snapshot time, and version. Never backdate an entry to a candle close observed later.
- Require fresh connected-demo quotes and candle exports (age <15 seconds), synchronized series and no missing M5 bars across the active setup. A gap/disconnection cancels the setup; reconnecting cannot revive it. Entries stop until at least two new contiguous completed M5 bars arrive after recovery.
- Broker-server candle timestamps remain explicitly labeled; elapsed holding time uses monotonic local time. Daily risk accounting uses Asia/Manila calendar dates. Do not infer historical UTC conversion from the current server offset.
- Historical bars downloaded at startup provide context only. Do not execute historical setups from that preload.

## 2. Register levels before the setup

The user registers each level with a side (support/resistance), price L, M15 evidence bars, creation time and unique ID. Levels cannot be moved after activation. Editing creates a new ID and cancels its pending setup.

Tolerance delta = 0.0005 × L (0.05%). Protective-stop buffer b = 0.00025 × L (0.025%). These scale with the registered level and stay fixed for its lifetime.

Eligible level evidence:
- At least two reactions among the last 96 completed M15 bars.
- Touch: candle range intersects [L-delta, L+delta]. Touch bars must be separated by at least three M15 bar openings.
- Resistance reaction: touch candle closes at or below L, then at least one of the next three completed M15 candles closes at or below L-2delta.
- Support reaction: touch candle closes at or above L, then at least one of the next three completed M15 candles closes at or above L+2delta.
- Every evidence and reaction-confirmation bar must already be completed and received at registration. Save their timestamps/OHLC. Retrospective marking cannot qualify an earlier breakout.
- Level expires 24 elapsed hours after registration, or after one breakout attempt, whichever occurs first. No automatic rearming. The user may later register a new level with current evidence.
- Candidate target levels must be registered before the breakout too; no inventing a favorable target after seeing price move.

## 3. H1 context filter

At breakout and again at entry, use the latest two completed H1 bars available then:
- Long permitted only if latest H1 close > previous H1 high.
- Short permitted only if latest H1 close < previous H1 low.
- Otherwise no entry. Equality is not a pass.

This intentionally simple filter is a new experiment, not the video's exact context rule. No volume filter, extension filter or discretionary size reduction is included.

Before activation the user must explicitly mark event context reviewed. A user-marked news pause prevents entries; there is no automated news feed. Manual review remains a recorded input, not an objective algorithmic finding.

## 4. Long setup

1. Registered resistance L must be active and context reviewed.
2. Breakout: a completed M5 candle closes > L+delta and its immediately preceding completed M5 close was <= L+delta. H1 long filter passes. Consume the level's one attempt.
3. Retest must occur in the next six completed M5 candles after breakout (breakout candle excluded; sixth included).
4. A retest candle range intersects the tolerance band. Every post-breakout low through confirmation must remain >= L-delta, and every post-breakout close must remain >= L. A deeper wick or close below L cancels the attempt.
5. Confirmation: the retest candle itself or a later completed candle within that same six-bar window closes > L+delta and close > open. Retest must already have occurred; future candles cannot retroactively confirm it.
6. Stop = lowest low of all completed post-breakout M5 candles through confirmation, minus b. Breakout candle itself is excluded. Round stop down to valid tick size.
7. Hypothetical entry = first fresh executable ask quote RECEIVED after confirmation was detected, with a modeled adverse entry slippage. It must arrive within 10 seconds of detection, and not more than 15 seconds after the expected broker bar close. Otherwise skip. This is a latency constraint, not a guaranteed fill.
8. Target = nearest registered eligible resistance above entry, excluding the traded level. Round target down to tick size. No target, or insufficient net reward, means skip. Do not bypass a closer eligible obstacle in favor of a distant one.

## 5. Short setup (mirror)

1. Active registered support L and context reviewed.
2. Completed M5 close < L-delta; preceding M5 close >= L-delta; H1 short filter passes.
3. Retest from below within the next six completed M5 candles.
4. Every post-breakout high through confirmation <= L+delta; every post-breakout close <= L. Otherwise cancel.
5. After band contact, a completed bearish candle closes < L-delta within the same window.
6. Stop = highest post-breakout high through confirmation + b, rounded up to tick size.
7. First fresh received bid after confirmation plus adverse slippage, using the same latency bounds.
8. Target = nearest eligible registered support below entry, excluding the traded level; round up to tick size. Require sufficient net reward.

## 6. Costs, sizing and eligibility

- Use verified contract size, tick size, minimum/maximum volume and volume step from broker specifications. The current exporter does not yet include all these fields; extend and verify it before paper-engine activation.
- Commission must be explicitly configured and confirmed for the account. Unknown is NOT zero. Record amount, per-side basis, currency and source/date.
- Initial slippage stress assumption: USD 5 per BTC per fill, adverse on entry and exit. This is a simulation assumption, not measured Exness execution quality.
- A quote-derived entry already includes the entry side of spread. Model long exits on bid and short exits on ask. Do not deduct a second full spread on top of executable bid/ask fills.
- Calculate planned stop loss and target gain after commission and adverse fill assumptions. Require net potential reward / modeled stop loss >=2.0. No partial targets, break-even moves or trailing stops in v1.
- Research paper balance starts USD 1,000. Per-trade planned risk budget = min(USD 5, 0.5% of current paper equity). Round size DOWN to broker volume step, then check minimum, maximum and margin feasibility. Skip if no valid size fits the budget. No leverage increases to rescue an ineligible position.
- One open paper position across both directions, no averaging, no pyramiding and no simultaneous opposing positions.
- Pause new entries after daily realized losses total USD 20 (sum of negative net closed results, not offset by wins), or after three consecutive losing closes. An already open position retains its exits. A triggered pause lasts until next Asia/Manila date and explicit resume; restarting the app must not reset it.
- These limits are experiment settings, not a recommendation for real funds. Stops can gap; the budget is not a guaranteed maximum loss.

## 7. Paper exits

- Long protective stop triggers when observed bid <= stop; short stop when ask >= stop. Fill at the adverse side of the observed quote and stop level, with adverse exit slippage. Never assume a gap fills at the stop price.
- Target triggers when long bid >= target or short ask <= target. Cap favorable fill at target, then apply adverse exit slippage. Commission applies as configured.
- Maximum hold: 30 elapsed minutes from entry. Close at the next fresh executable quote with exit slippage. A missing quote delays the exit and is recorded, not assigned a fabricated price.
- No discretionary stop widening. No reversal into another trade on the same tick.
- If quotes go stale while a position is open, stop new entries, flag execution uncertainty, and wait for the next fresh quote. Quote polling can miss intrainterval touches: label these results POLLING-BASED / NOT TICK-COMPLETE. They are not equivalent to broker-hosted stops.
- Candle-only historical replay: when stop and target are both inside one bar and order cannot be known, mark AMBIGUOUS and count stop-first for conservative summary; retain the ambiguity flag and report its count. Do not use M1 to choose a favorable sequence in v1.
- Closing once is atomic and idempotent. Log trigger, quote, receipt time, expected fill, costs and net P/L.

## 8. State machine and records

DRAFT → ARMED → BREAKOUT_CONFIRMED → RETEST_SEEN → ENTRY_ELIGIBLE → OPEN → CLOSED.
Terminal setup outcomes: EXPIRED, INVALIDATED, CONTEXT_FAILED, DATA_GAP, STALE_FEED, COST_FAILED, SIZE_FAILED, NO_TARGET, USER_CANCELLED, MISSED_ENTRY. Every failure gets a timestamp and reason. No terminal setup is revived.

Store level/evidence IDs, user context review, frozen parameters, H1 snapshots, breakout/retest/confirmation bars, source provenance, entry/stop/target, specs/fees, fill assumptions, risk gates, and exit reason. Identical input events must yield identical decisions. Deduplicate by symbol, level ID, direction and breakout bar time.

## 9. Verification before activation

- Independent check of representative completed M5/M15/H1 OHLC against MT5, beyond current exporter-to-app equality; confirm candle price basis.
- Unit cases for long/short boundaries, exact expiry/equality, forming-bar rejection, no-lookahead level evidence, spread accounting, rounding, gaps, simultaneous touches, restart recovery and duplicate events.
- Replay fixture with expected states and skipped reasons, then live demo forward observation. Freeze this version and keep evaluation data separate from any tuning.
- Present net P/L, drawdown, trade count, costs, ambiguity count and data gaps. No target win rate, profit promise or minimum sample count establishes an edge by itself.

## 10. Review gate

This is the user-approved v1 baseline. Its specification and parameter hashes are frozen before paper testing. Implementation and data verification are reported separately from approval. Later rule changes create a new candidate and separate results. No live broker trading is included.
