# v1 implementation record

Approved baseline: frozen/manifest-v1.json. Frozen numeric rules have not been tuned to observed performance.

Implemented in backend/engine.py and backend/paper_service.py:
- Manual levels validated against completed M15 reaction evidence; immutable IDs and terminal outcomes.
- H1 direction, completed M5 breakout/retest, exact six-bar expiry and strict confirmation inequalities.
- Subsequent-quote entry with detection/bar-close expiry; no preload execution.
- Closest pre-registered target; side-correct quotes, tick/lot rounding, commission, margin/size and 2R gates.
- One paper position, adverse gap stops, capped target fill, 30-minute monotonic hold timer.
- Feed-gap uncertainty, two-new-bar recovery, persistent daily/consecutive-loss pause.
- Atomic state, durable audit and idempotent closes. Conservative candle ambiguity helper.

Not asserted complete by code tests:
- Independent MT5 visual candle parity (user must confirm and record).
- Actual updated broker specification receipt (indicator reload required).
- Actual account commission (explicit user source/date required).
- Live forward-trade coverage; no setup has been forced or fabricated to claim success.
- Tick-complete historical replay/performance reporting; the candle ambiguity helper is a diagnostic, not a historical backtester.

Engine activation remains off until prerequisites are verified. No broker-order execution code exists.

Published Standard account fee research is saved in commission-research-2026-10-19.md. UI can prefill USD 0 and its official source; it does not mark account-specific confirmation or candle parity on the user's behalf. The rate is conditional on Standard account type.

Runtime integration verified: after user attached BTCStudioMargin (a read-only Expert Advisor calculation helper), fresh buy/sell one-lot margin estimates arrived. MT5 prohibits OrderCalcMargin in custom indicators, so that unsupported call was removed from quote-indicator source and delegated to this helper. No OrderSend/CTrade is used. Algo Trading stays off.

Broker candle basis, tick size, lot limits, currency and helper margin fields are now verified in the actual feed. Manual candle parity/account commission checks remain separate prerequisites. No generated trades or strategy results are claimed.
