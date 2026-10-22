# BTC Studio

Local Bitcoin research and manual paper-trading app, based on the approved dark red/green mockup.

## Open

http://127.0.0.1:5173 (frontend), with Python API on 127.0.0.1:8000.

For future sessions, double-click `start.command` in Finder. Keep its terminal open. Closing it stops the services it starts. Do not start a second instance while the existing app is running.

## Features

- React + TypeScript dashboard, Tailwind, Lightweight Charts, library icons.
- Deterministic sample candlesticks, M5/M15/H1 views and manual next-bar replay.
- Manual level marking and four-step confirmation checklist.
- Python/FastAPI risk planning, costs, conservative lot-step rounding.
- SQLite paper-trade/observation journal, manual closes, JSON export.
- Settings and transparent strategy limitations.

## Important scope

**Not live trading. No broker order endpoint exists. No credentials are stored.**
Sample bars are synthetic, not historical Exness prices. Timeframe samples are independent and not aggregations. Current replay position and unsaved planner inputs reset on reload; journal entries persist.
The checklist is manual, not computed from candles. Strategy rules remain a draft and are UNPROVEN. No backtest, automated signal, automatic stop/target exit, or enforced daily-loss limit exists yet.
Paper entries use the user-entered hypothetical price. Manual exits use the displayed sample close. This is a planner/execution prototype, not a validated fill simulator.
Sizing assumes 1 BTC/lot, 0.01 minimum/step and zero commission. One spread charge plus slippage on both fills is deducted, in USD per BTC. Actual broker specs/fees are not verified. Risk is a budget, not a guaranteed maximum loss.

## MT5/Wine bridge — compiled and installed; awaiting chart attachment

`mt5/BTCStudioQuotes.mq5` is a read-only custom indicator, compiled with the installed MetaEditor (0 errors, 0 warnings). The EX5 and source were installed under MT5's `MQL5/Indicators/BTC Studio/` folder. No trading functions or network calls exist in the indicator. Algo Trading can stay off.

In MT5 Navigator, refresh Indicators, expand BTC Studio, and attach BTCStudioQuotes to the BTCUSDm demo chart. Leave ExportSymbol as BTCUSDm. Once ticks change, it exports `btc-studio-quotes.json` every two seconds in Common Files.

The Python service reads the existing Wine Common Files directory for user `user`, using the exact quote filename only. Override with `BTC_STUDIO_QUOTE_PATH` if the MT5 installation changes. No separate copy/import process is needed.

Settings polls the service every two seconds, displays bid, ask, spread and specifications, and labels values fresh only if both export and last observed tick change are under 15 seconds old, terminal is connected, and account is demo. An initial unchanged cached quote is not treated as fresh. File writes can be briefly incomplete; those are rejected and retried on the next poll.

Live receipt has NOT yet been verified. The dashboard chart and planner remain synthetic/manual even when the quote panel is connected. No live execution is possible.

Legacy BTCStudioSnapshot.mq5 and import_snapshot.py remain archived source examples; use BTCStudioQuotes instead.

## Development

Python 3.9+, Node 20+.

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cd app
npm install
```

Run backend from the project root with `.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`; run frontend with `npm run dev -- --host 127.0.0.1 --port 5173 --strictPort` from app/.

Validation: `.venv/bin/python -m pytest backend/test_core.py -q`; `npm run build` from app/.

The local database `backend/studio.sqlite3` is ignored by Git. The first two journal entries are labeled QA samples from browser verification, not strategy evidence.

## Candle export update

The current BTCStudioQuotes indicator exports up to 400 M1/M5/M15/H1 OHLC bars in `btc-studio-candles.json` alongside quotes. Remove and reattach the indicator after replacing its EX5. History may take several timer cycles to download. M1 is not selectable for strategy entries.

Overview defaults to **Exness demo candles**. It never substitutes synthetic data when the export is missing or invalid. **Sample replay / paper execution** remains a separate source. Trade opening/closing is disabled in broker-chart mode to avoid mixing prices with the sample fill model.

The last candle is forming. Timestamps are exported and plotted as MT5 broker-server clock values, not converted to UTC. The observed server/UTC offset is included in the source snapshot; historical DST offsets are not inferred. Candles are read via MT5 CopyRates. Valid fresh snapshots are archived (upsert by symbol, timeframe, broker time) in SQLite `broker_candles` while the app is polling Exness mode. This is a rolling archive, not a guaranteed gap-free historical data service. No volume filter is added.

Current verification: indicator compiled with 0 errors/warnings; actual fresh exports received after reattachment, with 400 bars per timeframe. Completed M5/M15/H1 OHLC values match the exporter snapshot and SQLite storage was verified. Browser shows Exness candles and updating prices. Independent visual comparison against the MT5 chart remains separate from this delivery check.

## Approved v1 paper engine

The user approved the baseline on 2026-10-19. Immutable rule/parameter files and approval manifest are in `strategy/frozen/`; the engine checks their SHA-256 integrity. Original review proposal is preserved separately.

Strategy now provides the engine status, prerequisite form, M15 reaction evidence selection, level registration/cancellation, start/pause/news controls, separate engine trade history, and full JSON audit export. It starts PAUSED. Starting requires fresh synchronized demo data, verified broker chart basis/specs, explicitly confirmed commission (with source/date), and a recorded independent completed-candle comparison. No rate or verification is fabricated.

The read-only exporter now also provides bid/last chart basis, tick size, max volume, USD account currency and account currency. Read-only one-lot margin estimates are exported separately by BTCStudioMargin (under Expert Advisors/BTC Studio), since MT5 prohibits OrderCalcMargin in indicators. Keep Algo Trading off; this helper contains no OrderSend or trading library.

The Python service evaluates every two seconds independently of whether the Strategy page is visible. It persists paper state and event audit transactionally in `paper_engine` and `paper_audit`. Live-paper engine results are separate from the original synthetic manual journal and start at $1,000 virtual equity.

Open paper positions get side-correct quote exits, configured commission and adverse fill assumptions; no duplicate spread deduction. Time exits use a monotonic timer within a service run. On restart pending setups are cancelled, open positions get an uncertainty marker, and the remaining hold duration is recovered conservatively from persisted UTC deadline (clamped to 0..30 minutes). This recovery is explicitly audited. Risk pauses survive restarts and require a later Manila date plus explicit resume.

Quotes are POLLING-BASED / NOT TICK-COMPLETE. Intrinterval stop/target touches can be missed; actual broker execution is not simulated perfectly. No performance or profitability validation is claimed. Commission, independent visual parity and updated broker fields are prerequisites before forward-testing; Strategy lists what is still missing.

Engine tests: `.venv/bin/python -m pytest backend -q`.

Margin helper runtime verified after user attachment: fresh USD buy/sell one-lot estimates received. Paper-engine activation still waits for recorded candle parity and account-specific commission confirmation.
