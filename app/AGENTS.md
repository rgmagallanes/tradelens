# Prototype Instructions

Run the local server yourself and open the preview in the browser available to this environment. Do not give the user server-start instructions when you can run it.

Before making substantial visual changes, use the Product Design plugin's `get-context` skill when the visual source is unclear or no longer matches the current goal. When the user gives durable prototype-specific design feedback, preferences, or decisions, record them in `AGENTS.md`.

When implementing from a selected generated mock, treat that image as the source of truth for layout, component anatomy, density, spacing, color, typography, visible content, and hierarchy.

Build app UI in `src/`. Keep `.openai/hosting.json`, `worker/index.js`, `scripts/prepare-sites-build.mjs`, and `tests/sites-worker.test.mjs` intact so the same local prototype can be handed to Sites. Before a Sites handoff, run `npm run build` and `npm run test:sites`; the build must leave `dist/client/index.html`, `dist/server/index.js`, and `dist/.openai/hosting.json`.

Journal: provide a dropdown for loading fictional demo datasets. Keep demo data separate from saved manual/paper journals and clearly labeled; never seed demonstration trades into the user's records.

Journal reporting: support Monday–Sunday weekly reports, calendar-month reports and calendar-quarter reports, anchored to the selected day and using Asia/Manila closing dates. Day selection should expose a chart review. Keep recorded historical context distinct from entry-time screenshots; preserve saved chart-review candles/markers and show missing coverage explicitly. Demo charts and reports must remain fictional and isolated.

Overview: include H4 (four-hour) candles and a green/red tick-volume pane beneath price. Label broker tick volume as quote activity; synthetic replay volume must be marked synthetic. Missing volume/H4 data must not be fabricated or silently replaced with sample data.

Overview Technicals: retain three semicircular gauges (Oscillators, larger Summary, Moving Averages), driven by the selected timeframe and completed candles. BTC Studio uses its own disclosed indicator rules; do not imply TradingView parity, win probabilities or automatic trading. Missing, stale and synthetic data must be labeled.

Technicals refinement: include labeled timeframe buttons above the gauges synchronized with Overview (M5/M15/H1/H4). Summary rating text enters from below with short ease-out motion when timeframe/rating changes; honor reduced motion.

Gauge transitions must ease directly from the last score to the next; never reset through zero during timeframe loading. Reserve loading/status/availability space so Technicals height stays stable.

Technicals: show Oscillators and Moving Averages Name/Value/Action tables beneath the gauges, side by side on desktop and stacked on phones, sourced from the same current model.

Expanded Technicals model has 11 oscillators and 15 MA/filter votes (26 total). Require 200 consecutive completed bars plus valid tick volume for the full summary. VWMA is tick-weighted quote activity; never imply exchange traded volume or exact TradingView parity. Added votes remain descriptive only, outside the paper engine.

Pivots: display Classic/Fibonacci/Camarilla/Woodie/DM R3–S3 under Technicals, separate from gauge scores. Basis is previous complete UTC day reconstructed from selected-timeframe candles; Woodie uses current UTC day open. Reject partial daily coverage, never substitute a partial intraday range. DM only defines P/R1/S1.

Overview chart supports a full-window expanded view with persistent chart/timeframe/source/marked-level controls. Escape and Exit fullscreen restore normal layout and focus; preserve chart instance and lock background scroll while expanded.

Overview chart includes a Moving averages On/Off control with EMA/SMA choice and20/50/200 line legend, usable in fullscreen. Use completed contiguous candles; reset warmup at gaps. These chart overlays do not change strategy execution.

Desktop navigation supports a persistent collapse/expand preference:178px labels or68px icon rail, with accessible names and title tooltips. Retain existing mobile navigation layout.

Overview instrument selector supports BTCUSDm and Gold XAUUSDm. Gold reads its own xau-studio quote/candle files through GoldStudioQuotes; never substitute BTC/sample candles. Clear source data/levels on instrument change. Gold is read-only chart/indicator/pivot review; BTC sample sizing and engine remain BTC-only.

Gold technicals and MA overlays are bar-based across exported session/time gaps, with explicit gap/coverage disclosure; never fill missing bars. Bitcoin retains strict contiguous suffix logic. Both exclude forming bars and invalid data.

MT5 auto-journal: use a distinct read-only mt5 source, isolated from manual/engine/sample records. Demo USD hedging UTC+0 accounts only in v1. JournalStudioTrades exports seven-day exits plus full lifecycle for related/open positions; importer pins a hashed account identity, upserts unique deal IDs, allocates entry costs to partial exit fills and reconciles residual volume. Closed fills count separately. Display sync freshness/issues and a zero-based imported P/L ledger, never claim it is account balance. Cash movements/account-level adjustments and open floating P/L are excluded; no broker execution is allowed. Daily notes remain editable; imported fills are read-only. Gold review may use its own existing candle archive.

MT5 journal shows Running positions near sync status: each reconciled open position lists symbol/side/lots/entry/open time and signed floating trading P/L, plus combined USD total. Poll status every5s, mark retained values stale when disconnected, and exclude floating P/L from realized calendars/reports. POSITION_PROFIT excludes swap/commission/fees; label this explicitly.

MT5 selected-day trade cards each show their own floating P/L from the live position ID, and a Review this trade toggle. Chart reviews and saved snapshots are keyed by source/trade ID/timeframe; do not reuse the day-wide snapshot or show other trades in a specific-trade review. Keep daily totals separate.

MT5 calendar cells show current open-position count and floating P/L grouped by Manila entry day, separately labeled from closed daily net results. Never add floating values into daily realized totals. Stale feed values must be marked, missing amounts unavailable, and day click exposes individual trade cards.

Product name is TradeLens. Approved subtitle: “See the setup. Track the trade. Review the result.” Use both in the app header and TradeLens in browser title/visible product copy and journal exports. Retain existing MT5 helper names/folder paths and stored-data keys for compatibility.

TradeLens header visual direction: gold-accented Trade/Lens wordmark and lens/candlestick emblem, preserved approved subtitle, selected-instrument bid/ask module and compact workspace breadcrumb/feed status strip. Keep demo/no-broker-orders visible; use only matching instrument quotes, show stale/waiting clearly and hide broker values in synthetic replay. Responsive two-row phone layout.

Header P/L: show signed all-account MT5 demo floating P/L and Closed today (Asia/Manila imported realized net) separately, refreshed every5s. All-symbol scope stays explicit independent of selected chart/replay. Missing export is unavailable, stale values labeled last reported; exclude floating swap/fees and do not combine unrealized with realized results.

Journal reports include a TradeLens performance radar and custom v1 score, not Zella’s formula. Six equally weighted normalized metrics: win rate, PF capped at2, average win/loss capped at2, recovery capped at3, drawdown control100/(1+DD/mean absolute trade P/L), profitable-active-day consistency. Require20 closed fills/trades across5 active days plus all metrics defined; withhold missing headline values and never fabricate infinity/zero ratios. Show source, fictional demo, partial-exit-fill semantics, raw metrics and full formula explanation. Score follows selected report period/source and exports its versioned profile. It is descriptive, not proof of edge or win probability.

Calendar day previews appear on pointer hover or keyboard focus, one at a time. Show closed net P/L, counts/win rate, balances, up to3 closed fills, note excerpt and separately labeled current/stale floating values. Escape dismisses, pointer can move into preview, portal is clamped to the document viewport; touch tap/click still selects full day review.

Overview includes an FVG On/Off overlay for BTC and Gold on all chart timeframes/fullscreen. Detect strict contiguous three-completed-candle wick gaps, shade bullish green/bearish red, extend right, and remove only on a later completed candle's full wick fill. Partial fills retain original bounds. Display latest30 unfilled zones from loaded history; do not imply order flow, institutional positions, trade signals or guaranteed fills.

Closed trades have an AI Trade Review panel: independent local facts/checklist, retrospective plan/reflection, immutable source/trade-keyed review snapshots and JSON export. Do not infer original stops/targets from final broker fields. Price R excludes costs; MFE/MAE are whole holding-period M5 bid-chart estimates with missing coverage disclosed and boundary/post-exit candles excluded. Optional OpenAI generation requires server-only configuration, payload preview, explicit per-request consent and unchanged evidence fingerprint; no automatic sends or paid calls during QA. Unknown keys/models disable generation; local work remains available. AI coaching must stay educational and evidence-limited, with one experiment rather than a profitability promise. Fictional demo records remain read-only.

Header Account balance uses only MT5 ACCOUNT_BALANCE from JournalStudioTrades, in the same validated account snapshot as P/L. Optional field for old exports; never reconstruct from the zero-based P/L ledger, trades or paper balance. Show waiting until exporter updated, last-reported when stale; keep floating P/L separate. Phone header fits three metrics.

Journal Trade plans & ideas: create immutable server-timestamped original plans (source, symbol, side, setup/reason, planned entry/stop/target, declared total USD idea risk budget) before execution. Capture only matching already-archived completed M5 candles as frozen plan-time context; missing/stale context is explicit, never an asserted entry screenshot or broker execution proof. Group multiple matching-direction/symbol positions with source isolation. MT5 assignment follows POSITION_IDENTIFIER across partial exits and open remainders, with association audit, not transient trade-row IDs. Preserve all execution records and unchanged calendar/report totals; all-date group realized and floating P/L remain separate. Plans linked after an older entry are retrospective based on server save vs earliest linked entry, regardless of link time. Linked immutable originals can supply postmortem evidence; later review-note risk overrides are explicitly retrospective and never overwrite the original. No automatic AI calls, exposure enforcement or orders. Demo dropdown records stay read-only.

Calendar has a rightmost weekly P/L card aligned with each Monday–Sunday row, showing signed closed net P/L, closed execution count and active closed-trade days. Boundary weeks include visible-month days only; floating P/L remains excluded. Weekly totals reconcile to visible month/source/demo dataset. Use green/red/neutral text, exact amount/date-range title and accessible label. On narrow phones scroll only calendar grid horizontally; never overflow the whole page.

Calendar monthly total sits directly below the rightmost weekly cards, reconciled from visible-month daily closed net P/L in integer cents. Follow selected source/month/demo and keep floating excluded; retain exact amount in accessible label/title.

Equity Flight in Journal: lazy-loaded Three.js flight path uses selected-month daily closed P/L accumulated from zero in integer cents; no fabricated account equity or floating values. Daily-close drawdown is not intraday drawdown. Explicit fictional/demo labels, 2D fallback, manual checkpoint selector, optional play/pause, day review link. Render on demand and dispose GPU resources on unmount.

Build your farm replaces Equity Flight: approved warm isometric farmhouse/barn/orchard/pond diorama. Animate articulated builders and gardeners, wandering chickens, swimming ducks and grazing cow. Decorative construction/crop progress follows review checkpoints, never financial returns; exact selected-source monthly P/L remains separate. Pause/resume animation, respect reduced motion, suspend offscreen/hidden rendering, dispose GPU resources. Maintain day log fallback, replay slider/checkpoint and day review; do not change navigation or invent live data.

Farm loss reaction: default to latest closed-day checkpoint. When selected checkpoint cumulative monthly closed P/L <0, display reversible stylized barn flames/smoke with firefighting crew. At >=0 clear fire and restore builders. Label trigger clearly; this is selected-source monthly P/L from zero, not MT5 account balance, floating P/L or irreversible damage. Pause/reduced-motion applies to effects.

Ambient visual direction: charcoal foundation with static soft violet/magenta blooms behind top-right header and lower-left workspace, lightly translucent dark panels and muted violet borders. Preserve gold branding, red/green financial semantics, quiet chart/farm rendering, all layout and interaction behavior. Use ambient.css loaded after base styles; no animated background or broad blur filters.

Main navigation order: Overview, Journal, Strategy, Replay. Journal occupies the second position on desktop and mobile.

Hosted deployment is a separate server/ Node.js+MySQL journal release, not a port of all Python features. server build sets VITE_HOSTED=true and serves the compiled frontend from the same origin, gated by private invited login. Local Vite/Python remains unchanged by default. Tenant IDs come only from server sessions; imported trades use revocable device tokens and account pinning. Do not claim cloud chart/research/AI parity or automatic sync. Never put DB credentials, invitations or device tokens in Vite variables or Git.
