# Scalping comparison: breakout/retest versus trend-pullback

**Exploratory / UNPROVEN. Neither candidate demonstrated profitability.**

Same frozen Exness demo BTCUSDm data: 2026-10-12 12:00 through 2026-10-19 12:00, MT5 broker-server time. 10,068 completed M1 candles; one 12-minute gap. All four runs use the same window and starting modeled equity of USD1,000.

| Strategy | Assumed spread/BTC | Closed trades | Modeled net P/L | Realized drawdown |
|---|---:|---:|---:|---:|
| Breakout/retest v2 | $6.40 | 3 | $-6.55 | $6.55 |
| Trend-pullback v3 | $6.40 | 0 | $0.00 | $0.00 |
| Breakout/retest v2 | $12.80 | 3 | $-6.11 | $6.11 |
| Trend-pullback v3 | $12.80 | 0 | $0.00 | $0.00 |

## Interpretation

Breakout/retest reproduced the existing result: three losing trades on 13 October, then a run-long three-loss pause. The final two-day segment remained untraded because of that pause. Doubled spread caused smaller lot rounding, explaining the smaller dollar loss; it did not improve fills. Modeled spread/slippage costs were $1.97 and $2.28 respectively.

Trend-pullback v3 tested M15 EMA direction, confirmed M5 rising/falling swing structure, a held swing-level pullback, then M1 minor-structure confirmation. It created 79 attempts: 44 reached confirmation but failed the 2-net-R cost/reward gate, 19 expired, and 16 invalidated. Two additional touches were rejected for no target before an attempt was created. No positions opened under either spread assumption, so there is no win rate or profitable-trade evidence. Zero P/L with zero trades does not establish that it is a better trading strategy.

## What was fixed before this run

Rules were written in `strategy/trend-pullback-research-v3.md` before the first v3 replay. No parameter search, post-result rule relaxation or live settings changes. Both candidates retain 2 net R, risk min($5,.5% equity), next-M1-open entries, one position, 30-minute time exits, $5 adverse slippage/BTC/fill and the run-long risk pause. Pivots require two completed right-hand candles and must be known before the touch candle opens. Targets are frozen at activation.

Both candidates use bid OHLC and assumed constant spreads of $6.40/$12.80 with modeled zero commission and current lot/tick conventions. Historical margin, quotes, latency and news review are unavailable; this is not a verified execution backtest. None of the runs had an ambiguous stop/target bar, uncertain open-gap position or end-of-data open position. Drawdown measures closed equity only.

## Sample limitations and next research step

The same week has already been viewed and used for other experiments. First-five-day / final-two-day breakdowns in JSON are descriptive, not clean out-of-sample validation. Three closed trades cannot establish an edge. Keep these rules frozen and test a separate, earlier period before deciding whether either candidate merits forward demo testing. Obtain historical bid/ask or recorded quotes to improve execution-cost realism. Do not interpret the synthetic integration-test profit/loss as market performance.

## Verification and reproducibility

38 backend tests passed, including pivot availability, pre-touch evidence, one-use swing attempts, adverse-wick invalidation, next-open entry chronology and 30-minute exit timing. No original approved-v1 files or live paper records were changed.

Source SHA256: `c94477e213d73f582a1231c5e3771ab0e10ad40dd79c73f4baa01db16d0cd6e3`

Specification `strategy/lower-timeframe-research-v2.md` SHA256: `5b2002ebfb584d14697d66fd18f18d85a6b885b3bc091183cdc2274f05293503`

Specification `strategy/trend-pullback-research-v3.md` SHA256: `6d6809349a883c9268568694c7c46934a216f083e247f51bd34937ca6c721abb`

Raw source: `research/exness-history-v2-2026-10-19.json`. Full runs and per-trade/setup logs: `research/scalping-comparison-2026-10-19.json`. Reproduce with `python -m backend.compare_scalping --input research/exness-history-v2-2026-10-19.json --output /tmp/scalping-comparison.json` from the project virtual environment.
