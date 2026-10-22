# H1 refinement research v11

Status: UNPROVEN, isolated research. Written before refinement outcomes are evaluated. No live configuration, approved v1, or frozen v10 rule document changes.

Preserve v10 as reference: prior20 completed H1-high/low close breakout, next-H1-open entry, Wilder ATR14 initial2ATR stop, opposite prior10-bar close exit next open. Same 19 Aug–19 Oct2026 12:00 broker UTC+0 saved data and warmup, initial1000 plus separately initialized10000 sensitivity. Planned risk0.5% current equity; min/step.01lot/max200; one position; no pyramiding or fixed TP. Three consecutive losing closes or2% initial equity cumulative negative closes pauses remainder of run. Do not loosen pauses, increase risk, narrow stops, lower lot minimums, or restart the simulated account to fabricate more trades.

Predefined profiles, no subsequent grid expansion:
1. baseline: exactly v10.
2. ema50: latest completed close above rising EMA50 for buys or below falling EMA50 for sells. EMA uses last100 contiguous completed H1 bars (or all available if fewer), seeds with mean first50 closes, then alpha2/51. Need at least55 bars so EMA slope is last value versus value5 bars earlier. Check on signal close and again using only completed bars before entry open. Missing-bar continuity or insufficient warmup fails the filter.
3. ema50_range: same filter plus signal candle high-low <=2 times ATR14 from the preceding completed candle. Signal candle is excluded from that range benchmark; equality passes. This tests late expansion/chasing, not a stop-size adjustment. Record failed filters and do not tailor thresholds after observing which trades win.

Compare each profile at constant spread6.40 and12.80, adverse5/BTC/fill slippage and zero modeled commission:12 continuous-run scenarios. Same historical funding and margin limitations as v10. No news filter added. If a filter removes the single large winner or reduces performance, retain/report that result. Do not choose a production winner from these already inspected two months.

Diagnostics:
- Record every minimum-lot rejection with minimum virtual equity required for0.01lot at0.5% planned risk. This is a feasibility measurement, not a deposit recommendation or leverage workaround.
- Show total closed P/L excluding unverified swaps, realized drawdown, open/uncertain positions, active versus risk-paused bar counts, per-trade records and filter rejection counts.
- Compute leave-largest-winning-trade-out P/L as a concentration warning, NOT a rerun or an executable alternate strategy.
- Holding-cost sensitivity is post-hoc accounting ONLY:0/10/30 USD per lot per24h, invented stress inputs not broker rates. Use held bar-opening elapsed time plus one hour for stop exits as conservative duration proxy; actual overnight charge schedule/triple days/eligibility and account equity feedback are not modeled. Never label this actual net funding performance.
- Exness official swap-free documentation says cryptocurrency eligibility depends on PA swap-free status and status can change; cannot infer user's historical status. Need account evidence before interpreting fully net returns.

All earlier period research and repeated use of this sample are selection bias. A more positive score on this reused sample is not independent validation. Freeze the candidate family and require a separate unseen period and forward demo next. No profit guarantee or activation. Preserve source/spec/code hashes and verify baseline scenario trade records reproduce v10.
