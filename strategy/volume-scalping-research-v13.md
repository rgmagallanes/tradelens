# Tick-volume scalping research v13

EXPLORATORY / UNPROVEN. Frozen before observing volume-filter results. Research only, no live activation or paper configuration changes.

Compare v12 EMA_TREND_RECLAIM baseline against the identical strategy with one additional entry filter: completed M1 signal candle tick_volume strictly greater than 1.5 times the arithmetic mean of the preceding 20 completed contiguous M1 candles. Exclude signal candle from denominator. Require valid nonnegative integer tick counts and positive denominator; missing data never passes. Entry remains next contiguous M1 open. No threshold sweep, target changes, or forced entries. Raw signals cached before volume filtering; never contaminate baseline cache.

Same fixed evaluation: 2026-08-19 12:00 UTC through 2026-10-19 12:00 UTC, with warmup. Starting balance $1000, risk min($5,0.5% current equity), one position, two full candles after exit candle, 10 entries/day maximum, daily pause after three consecutive losses or $20 cumulative negative closes, permanent $100 closed-equity peak drawdown stop. All v12 stop/target/timeout, gap handling, sizing and cost rules retained. News OFF and scoped v9 news ON, each with $6.40 and $12.80/BTC spread and $5/BTC adverse slippage per fill, zero commission. Funding/margin/fill realism remain unverified.

Use one new MT5 demo export including prices, tick_volume and real_volume. Compare both strategies on this same export. Audit common timestamps' OHLC against saved original source, report differences; fail comparison on changed/missing evaluation OHLC rather than silently compare different histories. Preserve both hashes. Real volume is diagnostic only. Tick activity cannot identify institutions or actual exchange traded quantity.

Report all eight runs including blocked runs, trades, win rate, net modeled P/L, costs, drawdown, risk stops, daily activity, gaps and open/uncertain positions. Full dates do not imply trading remained active after a drawdown stop. Same previously viewed period is exploratory, not unseen validation. No proof of profitability from a positive result alone.
