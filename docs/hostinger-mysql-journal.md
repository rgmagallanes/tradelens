# Hosted TradeLens journal — deployment and scope

The existing Vite-only deployment cannot execute Python. This release adds a separate `server/` Node.js app using your existing MySQL/MariaDB database, and serves the frontend from the same origin. The build copies client assets into server/public so runtime stays inside the Node app directory. Local Python/SQLite behavior stays unchanged.

## Included / deliberately not migrated

Included: invite-only login (default two users), sessions, separate user journals, notes, balances, reports, calendars, device upload tokens, explicit read-only live journaling, demo chart feeds, retained demo candle history and frozen trade/day chart-review snapshots. Each user's records and chart history are scoped on the server. No order endpoints. MT5 normalization remains in the local Python importer.

Not included: live-account chart feeds, paper execution/research engines, trade-plan grouping and AI postmortems. This is not full parity with the local app. Data reaches the cloud only while the separately authorized Mac uploader is running; watch mode uploads every ten seconds.

## Hostinger configuration (change only after local integration tests pass)

1. Keep a backup/export of your existing local journal. No automated SQLite migration is performed.
2. Set the Node app root to `server`, framework Express/Other, Node22+, install `npm ci`, build script `npm run build`, entry `src/start.mjs`. If the Express preset exposes no build-command field, the package postinstall hook runs the frontend build during dependency installation. This is a Node server deployment, not a Vite static-output deployment; do not use `dist/client` as a backend entry. The build accesses sibling `app/`, installs its dependencies and builds with `VITE_HOSTED=true`. Hostinger must retain the full repository checkout. If it restricts builds to the selected directory, stop and package the monorepo before deploying.
3. Privately configure environment variables from `server/.env.example`: `APP_ORIGIN=https://tradelens.chardee.dev`, DB_HOST=127.0.0.1 and DB_PORT=3306 for the Hostinger-managed Node app/database connection; exact, full prefixed DB_NAME and DB_USER, DB_PASSWORD, NODE_ENV=production, and a private random REGISTRATION_INVITE of at least32characters. MAX_USERS=2. Do not enter DB credentials in Vite variables or commit `.env` files.
4. Hostinger's Node.js MySQL guide specifies DB_HOST=127.0.0.1 rather than localhost (which can resolve to IPv6). This refers to the Hostinger server, not the user's Mac. See https://www.hostinger.com/support/connecting-a-hostinger-mysql-database-to-a-node-js-application/. We have not verified that connectivity. For remote DB networking require TLS (`DB_SSL=true`) and verified certificates; do not disable certificate verification or broadly allow all IPs. For provider-local DB connections follow the provider's supported network settings.
5. Import `server/src/schema.sql` once through phpMyAdmin into the newly created database. It creates only `tl_` tables and does not delete existing tables. Alternatively run `npm run migrate` with server environment configured. Runtime startup does not mutate schema automatically. Review the SQL before applying it. It is not a general migration framework for future schema changes.
6. Deploy and check `/api/health`: expected JSON `{ok:true,mode:'hosted-journal',version:1}`. Sign in/create your first invited account, then create your wife's separate account. Store invitation privately; rotate it after registration. No email reset flow is included; maintain server access for recovery.
7. Confirm two-account isolation and backups before importing any trading records. Hosting success/health alone is not proof of secure tenant isolation.

## Pair a Mac uploader

Sign in to the hosted site, choose My devices, name the Mac and create an upload token. Save it privately immediately; it is shown once and only its hash is stored. Revoking a device stops subsequent uploads.

On the Mac keep MT5 and the local Python importer running. Configure TRADELENS_UPLOAD_URL (the exact HTTPS site origin) and TRADELENS_DEVICE_TOKEN locally; never paste them into chat, commit them, or type tokens into a URL. Run `python3 server/scripts/upload-mt5.py` first: it reads SQLite read-only and reports counts, without sending anything. Run with `--send` only after reviewing the destination and approving upload of that account's demo trade history. The tool sends only normalized journal records and balance metadata, no broker password/login or order requests. Account identifier is the local importer's existing SHA256 fingerprint.

Each user is pinned to the first imported demo account. A different account is rejected. Repeated/equal or older export timestamps are rejected. Existing closed rows remain when later exports omit them; current open positions are replaced atomically. Imported P/L stays net as computed by the local importer. Server accepts only USD/demo protocol assertions from the paired device; it cannot independently attest broker authenticity.

## Security / operations limits

HTTPS required in production, HTTP-only Secure SameSiteStrict cookies; same-origin JSON mutations; no cross-origin CORS. Credentials hashed with scrypt; tokens hashed; auth/device rate counters stored in MySQL. SQL parameterized; user ID comes from session, never payload. Production logs omit request payloads, passwords, tokens and DB error details. DB credentials must have access only to this app's database. Hostinger must forward the intended origin/HTTPS correctly. Sessions last7days; sign out revokes the session. Set up scheduled cleanup of expired sessions/rate windows and regular provider database backups before long-term use. No automatic account recovery, MFA, or broad production security audit is claimed.

## Hosted chart uploads
The existing per-user snapshot now includes validated Bitcoin/Gold candles and quotes. No schema migration is required. Redeploy the server from the updated branch, then run the updated uploader:

```sh
export TRADELENS_UPLOAD_URL="https://tradelens.chardee.dev"
python3 server/scripts/upload-mt5.py --send --prompt-token --watch
```

Keep the local journal importer, BTCStudioQuotes and GoldStudioQuotes running on the same demo terminal. The standalone Mac kit instead uses `python3 run.py --send --watch` and imports its own journal export each cycle. Only allowlisted chart fields are transmitted. The token is prompted once and remains in process memory. Ctrl+C stops syncing. Updates run every 10 seconds; network failures retry on the next interval, authentication/validation errors stop. Missing symbols stay unavailable, stale quotes/candles remain explicitly stale. Research, paper execution and historical trade chart review remain local. No orders are sent.

## User-authored review tags
Closed journal trade/fill nodes support mistake and lesson tags (up to eight per category). These observations never alter broker executions. Local tags use a separate SQLite table; hosted tags use reserved `review` rows in the existing tenant-scoped `tl_trades` table. No hosted schema import is required. MT5 upload upserts do not replace reviews. Fictional demo tags are read-only. Connection summaries use unique dated trades/fills across the full selected month, exclude open/unknown P/L, and disclose sample size and overlapping tags.

## Automatic MT5 TP/SL record nodes
Rollback checkpoint before this feature: `5952032` (safe outstanding Mac setup software committed; editor swap excluded).

The updated JournalStudioTrades exports POSITION_SL/POSITION_TP for current demo positions. Remove/re-add it once after installing the compiled update, keeping Algo Trading off. Current explicit zero means Not set; omitted fields remain Unknown. Local SQLite retains timestamped open-position observations when values change. Exit-fill DEAL_SL/DEAL_TP describe closing-time values; prior observations are retained separately, never presented as proof of protection from entry. Reference: https://www.mql5.com/en/docs/constants/tradingconstants/dealproperties

The existing cloud upload preserves these versioned evidence fields and validates their chronology. No hosted database schema change is required. Restart any already-running uploader to load the updated importer when using the standalone Mac kit. Source-code local importer was restarted during verification. The refreshed kit is in output/TradeLens-Mac-Setup.zip. Trade nodes attach TP/SL record satellites; these are descriptive records, not a discipline score, trading recommendation or order controls.

## Hosted chart-review archive
Redeploy the current server before restarting the updated uploader. Startup creates two additive tables automatically: tl_chart_candles and tl_chart_reviews (requires CREATE TABLE privileges on the existing database). No new database is needed. Existing journal data is retained.
Every accepted demo upload archives completed BTCUSDm/XAUUSDm M5, M15 and H1 candles. The updated project uploader also backfills available broker_candles from its local SQLite archive on startup and at most once every five minutes after a confirmed backfill upload; bounded to 31 days and 3,000 bars per instrument/timeframe. The standalone Mac kit may have no SQLite candle archive; its current indicator exports still accumulate on the server. Missing historical candles stay missing.
GET /api/trading-journal/chart-review and POST to the same path support the existing frontend contract. All reads, archives, trade lookups and saved snapshots are user-scoped. Snapshots are immutable, keyed by source, day, symbol, timeframe and optional trade ID, and include a SHA256 fingerprint. Source labels disclose historical reconstruction, completed-bar coverage, Manila display time, gaps and marker limitations. These are not entry-time screenshots or evidence of broker execution. Manual trades may originate from another feed; synthetic samples and live accounts never receive substituted demo charts.
Validation: pure archive/coverage and snapshot tests, Python read-only backfill tests, typecheck/build, and the disposable MariaDB integration test verify upload/archive, tenant isolation, persistence across later uploads and frozen snapshot immutability. Browser rendering and actual production rollout must be verified separately.
