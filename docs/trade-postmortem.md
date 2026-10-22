# TradeLens post-trade review

In Journal, select the closing day, find a closed trade and choose **AI Trade Review**.

1. Read the calculated facts. Price movement and excursions are price units, not cash P/L.
2. Expand **Your original plan & reflection**. Enter the setup, entry reason, original stop/target, management changes and lesson. Unknown levels should remain blank. Save the plan to refresh risk metrics.
3. **Save local review** stores the calculated evidence and rule-based checklist without any external AI request.
4. When an AI connection is configured, inspect **Preview the data sent to OpenAI**, tick the disclosure for this request, and choose **Generate AI coaching**.
5. Saved reviews retain their evidence, generation time, provider/model and evidence hash. Changed inputs mark an older review as earlier evidence. The UI shows the latest 10 saved snapshots. Export downloads the displayed review bundle.

## Optional AI setup

The running Python backend needs these environment variables, configured privately by the server owner:

- `OPENAI_API_KEY`: server-only OpenAI API credential. Never paste it in a journal note, frontend environment variable, chat, screenshot, Git repository or browser field.
- `TRADELENS_AI_MODEL`: a Responses API model available to that API project that supports strict JSON Schema structured output. No paid model is selected automatically.

Restart the backend after setting the environment variables. `start.command` inherits its launch environment; it does **not** automatically load `.env` files. Hosting environment settings are appropriate when a private hosted backend is implemented. Do not expose the current unauthenticated local backend publicly as a deployment shortcut.

The page reports configuration presence only; a configured status is not verification of API key validity, model availability or billing. This build was tested with mocked provider responses, not a paid request.

Requests use the fixed `https://api.openai.com/v1/responses` endpoint, structured JSON output, a 60-second timeout, a 3,000-output-token cap, `store: false`, no tools and no automatic retries. The app saves validated output only. Provider errors/refusals/incomplete outputs leave earlier saved reviews intact. Duplicate generation for matching evidence reuses the saved result; one generation is allowed at a time per backend process.

Official API reference used: [Structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs).

## Evidence and limitations

- Only this trade's whitelisted execution fields, net P/L, calculated facts, user-entered plan/reflection, up to 60 pre-entry M5 OHLC candles and explicit limitations are sent. Account identity, tickets, credentials, unrelated notes, other trades and screenshots are excluded. User-entered notes themselves can contain personal data, so inspect the payload before sending. API usage may incur charges.
- Recorded final stop/target values are not assumed to be original. User-entered initial levels are retrospective self-report and do not change the imported trade.
- Price R is side-correct entry-to-exit movement divided by the self-reported original protective-stop distance, before costs. Planned reward/risk requires side-correct original stop and target. Neither is an account return.
- Excursion estimates use closed M5 candles wholly inside the holding interval. Entry and exit boundary candles are excluded to avoid using movement before entry or after exit. Missing bars stay missing; bid-chart estimates do not reproduce ask exits, spread, slippage, tick order or cash results. Complete holding bars can still omit a material move in either boundary candle.
- Scans are bounded to eight calendar dates. Longer holding periods have no excursion estimates. No post-exit prices are sent as evidence. Sample replay receives no substituted broker history.
- Each imported MT5 partial exit fill remains a separate reviewed record, not a claim about the entire position.
- Historical context is reconstructed, not an entry-time screenshot. News, emotional state, initial risk history, stop modifications and higher-timeframe alignment are not independently verified.
- The local checklist is explicitly not AI. AI coaching is educational, evidence-limited and can be wrong. Suggestions are experiments to validate on a separate after-cost sample, not trade signals, optimal hindsight exits, proven edges or profit guarantees.

Persistence uses `trade_review_plans` and `trade_postmortems`, keyed by source and trade ID. These tables have no execution effects and never modify broker records. Include them in SQLite backups. This remains the current single-workspace app; separate hosted users/accounts are a different deployment task.
