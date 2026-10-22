# Nasdaq CFD opening-range three-model test v3

EXPLORATORY / UNPROVEN. Frozen before first Nasdaq outcomes2026-10-21. Uses the unchanged signal, allocation and exit rules in ny-opening-range-three-models-v2.md. No model search or retuning from Nasdaq results; BTC outputs remain untouched.

Instrument: exact exported USTEC_x100m Exness demo CFD, NOT QQQ ETF or a universal US100 specification. Input research/exness-nasdaq-history-2026-10-21.json. UTC+0 demo bid OHLC, symbol chart_mode0, tick_size0.01. This matches v2's0.01 protective buffer; no tick scaling change required.

Opening range09:30–09:45 America/New_York, confirmation M5, entries M1, session ends11:30. Full120-minute coverage required; missing sessions skipped. Weekdays only, no US holiday-calendar exclusions; reported results apply to a weekday CFD clock anchor (a holiday may have different liquidity). Standalone models and combined allocation max3 trades/day, no overlapping positions; breakout→retest→reversal simultaneous priority.

Cost scenarios fixed from observed quote/specs, not historical spreads:
- Observed-spread scenario: ask29848.07−bid29846.95=1.12 index points +0.01 adverse slippage per side =1.14 round-trip points.
- Stress:2×observed spread=2.24 points +0.05 slippage per side =2.34 round-trip points.
- Commission is UNVERIFIED. Both scenarios assume zero additional commission. Results are conditional; they are not fully verified all-cost broker returns. No swap due to forced same-session close; unobserved account-level charges/latency/margin not modeled.

Report index-point P/L at fixed exposure and netR; no1BTC normalization, no account return, leverage or account-size assumptions. Exported contract_size100, tick_value1USD per0.01price tick perlot, min/step0.01lots are recorded but NOT used to claim feasible risk sizing. One observed quote cannot establish historical executable costs. Bid OHLC cannot reproduce short ask-stop triggers or tick ordering.

Use first70% of complete sessions and final30% with identical rules. Nasdaq results were not used to set this test, but rules were informed by earlier video interpretation and Bitcoin research; this is exploratory cross-market testing, not proof of a pristine holdout or edge. Preserve all models/scenarios and later-segment losses. No live/paper engine changes.
