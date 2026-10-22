# USTEC_x100m opening-range research — v3

**EXPLORATORY / UNPROVEN. Commission unverified; no activation.**

Export received2026-10-21 from NasdaqStudioHistory: exact broker instrument USTEC_x100m,64,593M1 bars, UTC+0 demo bid chart.47 complete weekday New York09:30–11:30 sessions,17August–20October2026; no incomplete sessions in this interval. This is a Nasdaq CFD, not the QQQ ETF.

The three models use the same signal/allocation/exit rules as the Bitcoin v2 test, without retuning from Nasdaq outcomes. [Nasdaq assumptions frozen before the test](../strategy/ny-opening-range-nasdaq-v3.md). No app/paper engine/order settings changed.

## All models, after modeled costs

| Model | Trades | Win rate (base) | Gross points | Net base points | Net stress points | Base PF | Base closed drawdown points |
|---|---:|---:|---:|---:|---:|---:|---:|
|Breakout|54|37.0%|+96.03|+34.47|-30.33|1.031|441.77|
|Retest|55|27.3%|-174.46|-237.16|-303.16|0.676|370.36|
|Reversal|16|37.5%|+163.89|+145.65|+126.45|1.416|176.44|
|Combined|88|30.7%|-85.53|-185.85|-291.45|0.896|553.47|

All P/L is cumulative index points at fixed exposure per trade, **not dollars, account returns, or a recommended trade size**. Do not compare point totals directly with Bitcoin dollars/points.

Base cost: observed1.12-point spread +0.01slippage per side =1.14points round trip. Stress:2.24spread +0.05slippage per side =2.34points. Spread was observed once at export, not reconstructed historically. Both scenarios assume zero extra commission, which is UNVERIFIED. Stress is a scenario, not an established upper bound on actual costs. Bid-based stop/target triggers cannot reproduce short ask stops, intraminute ordering or execution latency.

## Chronological stability

First32 sessions / final15 sessions from30September; identical rules, no tuning between segments. Exploratory cross-market sample, not proof of a pristine held-out edge.

| Model | Early trades | Early net points | Later trades | Later net points |
|---|---:|---:|---:|---:|
|Breakout|35|-117.14|19|+151.61|
|Retest|34|-275.88|21|+38.72|
|Reversal|7|-58.48|9|+204.13|
|Combined|56|-370.64|32|+184.79|

Reversal was positive overall in both scenarios (+145.65base /+126.45stress), but only16 trades, with an early loss and later gain. It is a candidate for more independent data/forward observation, not a proven profitable strategy. Base closed drawdown176.44points exceeds its total gain. Breakout+34.47base turns−30.33under stress. Retest and combined are negative overall. Combining all models did not create an edge.

## Candidate accounting

131 unique candidates:58breakout,57retest,16reversal. Standalone accepted54/55/16trades. Combined accepted88, excluding32overlap and11day-limit candidates; standalone counts cannot be summed as a portfolio. Same-minute priority breakout→retest→reversal, one position and max3 trades per session. All exits same session;0both-touch ambiguity cases.

## Limits and provenance

- Exact stock-selection/relative-strength rules from the video are not replicated. M1 reversal swing, displacement and zone definitions remain documented mechanical proxies.
- Weekday CFD09:30New York anchor; no exchange holiday-calendar exclusion. Higher-timeframe, volume and scheduled-news filters are not imposed.
- Source/spec hashes and all candidate/trade records are stored in the detailed JSON. Exported specifications include0.01tick,100contract size,1USD tick value per lot,0.01minimum/step; no lot/margin/account feasibility simulation was performed.
- No historical commissions/spread series, stop-trigger quotes, funding, receipt latency or independent fill records. No leverage or compounding.
- Shared runner now accepts exact instrument and explicit cost scenarios. All8 Bitcoin scenarios reproduced identical trades and metrics after generalization; original BTC outputs preserved.
-11 focused tests passed. Independent audit passed426 trade-scenario rows across8runs, including next-bar causality, OR/pivot/FVG/target evidence, fills, costs, daily caps and overlap rules.

[Detailed results](ny-opening-range-nasdaq-v3-2026-10-21.json) · [Independent audit](ny-opening-range-nasdaq-v3-audit-2026-10-21.json)
