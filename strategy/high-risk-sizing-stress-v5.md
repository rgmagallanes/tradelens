# High-risk sizing stress v5

UNPROVEN / isolated research only, written before this stress run. No live paper settings, approved v1 rules or broker execution changes.

Compare 0.5%, 1% and 2% equity planned risk per trade, with dollar caps $5/$10/$20 respectively, on initial simulated equity $1000. Fixed source snapshot, recent seven-day and earlier three-day windows, spread scenarios $6.40 and $12.80, $5 adverse slippage/BTC/fill. Keep the v4 EMA_TREND_RECLAIM signal and0.5 minimum net R identical in all runs. This candidate was selected after it had the highest observed recent-week win fraction; selection bias is explicit and this is not fresh validation.

The original $20 cumulative negative realized loss threshold and three-consecutive-loss pause remain fixed. Pause rest of each separately initialized research window only after closing losses cross the threshold. A threshold is not a guaranteed loss cap: a single loss, rounding, gaps, slippage and an already open position can overshoot. Higher sizing may pause earlier and suppress later trades. No martingale, averaging, forced trades or stop widening. Position limits and exit logic remain v4. Historical margin availability remains unverified, so larger positions may not be executable.

All signals and stop/target prices remain the same until changes to available capital/risk pauses affect later eligibility. Report planned sizing, P/L, closed-equity drawdown, N/wins, profit factor, fees, uncertainty, risk pause timing and source/spec/code hashes. Compare against v4 default reproduction. Do not claim that larger sizing increases win probability. No automatic winner or strategy promotion.
