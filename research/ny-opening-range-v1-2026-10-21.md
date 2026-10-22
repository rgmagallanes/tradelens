# Opening-range retest: first Bitcoin exploration

**EXPLORATORY / UNPROVEN — not ready for activation.**

Tested on saved Exness BTCUSDm demo history,17August–16October2026.45 complete weekday09:30–11:30 New York sessions;19October skipped because61 minutes were missing from the frozen export. DST handled with America/New_York.

Video basis: [Jdub opening-range strategy](https://www.youtube.com/watch?v=bITIVwysCzM). Our exact mechanical adaptation is documented in [the frozen research rules](../strategy/ny-opening-range-research-v1.md). No UI settings, original strategy, broker orders, or paper engine changed.

## Setup tested

1. Mark high/low of09:30–09:44 M1 bars, known at09:45.
2. First post-range M5 close above/below boundary determines direction.
3. Next10 M1 candles may provide a boundary touch and directional body/close. A close back inside cancels the candidate.
4. Enter next minute open, stop beyond retest extreme by0.01, fixed2R target, close by11:30. One candidate/trade per session; symmetric shorts are our adaptation.
5. No FVG, EMA, volume or news filter. Retest variant only; not a test of the video's breakout-gap or reversal entries.

## Results

| Scenario | Trades | Wins / losses | Win rate | Gross movement | Net after costs | Profit factor |
|---|---:|---:|---:|---:|---:|---:|
| Spread6.40 +1 slippage per side |7|3 /4|42.9%|−144.30|−203.10|0.60|
| Spread12.80 +1 slippage per side |7|3 /4|42.9%|−144.30|−247.90|0.53|

Movement is normalized USD price movement for1BTC exposure **per trade**, not an actual account return, a feasible trade size, or a recommendation. No leverage/margin/lot sizing/compounding is modeled. Costs are constant scenarios, not historical bid/ask quotes. Gross was already negative; costs worsened the outcome.

Chronological first31 sessions:4 trades, net+23.58 normal cost. Remaining14 sessions from29September:3 trades, net−226.68 normal cost. This history has already been explored in other research and is not pristine out-of-sample. Seven trades cannot establish a stable win rate.

38 complete sessions did not trade:17 retest timeouts,20 invalidated retests,1 no breakout. There were0 bars touching both stop and target. Conservative stop-first logic is implemented for that case.

The mean net R was+0.173 normal costs despite negative fixed1BTC P/L, because risk distances vary. Equal-exposure dollar totals and equal-risk R averages weight trades differently; neither is a tested capital-sizing system or evidence of a robust edge.

## What this tells us

The first exact retest adaptation is not profitable on fixed exposure in this small sample. It does not justify changing live settings, increasing leverage, or claiming the creator's broader discretionary strategy is disproved. Several decisive rules are ours: body confirmation,10-bar expiry, one-candidate limit, symmetric shorts, stop buffer and time exit.

A useful next exploration is a visual opening-range box with clearly labeled M5 confirmation and M1 retest markers, so missed/invalidated setups can be inspected. Any separate breakout-plus-FVG experiment should be defined before running, not adjusted repeatedly to turn this sample green. Gold requires its own sufficient M1 history and cost assumptions; this run covers Bitcoin only.

## Reproducibility

- Runner: `backend/orb_research.py`
- Detailed results, per-trade audit and hashes: `research/ny-opening-range-v1-2026-10-21.json`
- Four focused tests passed: next-bar causality, directional symmetry, both-touch stop-first, invalidation, incomplete session rejection, costs and DST.
- Audit confirmed all7 entries followed their M5 signal and M1 confirmation, targets were2R, and trade/no-trade counts reconcile to45 sessions.
