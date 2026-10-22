# Last seven days — exploratory setup replay

**UNPROVEN. Setup diagnostic only; no trade fills or profitability estimate.**

Period: 12 October 2026 11:40 through 19 October 2026 11:40, MT5 broker-server clock. Last completed M5 bar opened at 11:35. 2,015 completed M5 bars; one missing five-minute bar.

| Fixed level | Direction | Breakout candle | Outcome |
|---|---|---|---|
| 82,850 resistance | Bullish | 12 Oct 20:05 | Retest confirmed on 20:15 candle |
| 82,600 support | Bearish | 12 Oct 16:50 | H1 context failed |
| 82,400 support | Bearish | 12 Oct 17:25 | Invalidated after breakout |
| 82,250 support | Bearish | 12 Oct 22:55 | Retest window expired |

Times above are candle opening times. Confirmation becomes knowable only after candle close: the 20:15 M5 candle completed at 20:20.

The bullish pattern is not a qualified simulated trade: the tested map contains no higher resistance target. Historical executable bid/ask quotes, latency, manual news review and margin history are unavailable, so no P/L, drawdown, costs or win rate are reported.

These four price levels were selected after viewing recent history. Chronological evidence checks do not remove that selection bias. Each level was registered once when two already-completed M15 reactions became available, then allowed one attempt and a 24-hour lifetime. Levels were not automatically rearmed; this is not an exhaustive scan of every setup during the week. H1 and M15 candles were revealed only after their close; forming bars were excluded.

The raw export and JSON result are retained alongside this report. Existing live paper settings, positions and registered levels were not changed.

Verification: 27 backend tests passed, including replay-window boundaries and future-candle visibility checks.

Data gap: [{"after": "2026-10-18 07:30", "before": "2026-10-18 07:40", "missing_m5_bars": 1}]
