# Hosted journal release 1 — preparation, not deployed

The existing Vite-only deployment cannot execute Python. This release adds a separate `server/` Node.js app using your existing MySQL/MariaDB database, and serves the frontend from the same origin. The build copies client assets into server/public so runtime stays inside the Node app directory. Local Python/SQLite behavior stays unchanged.

## Included / deliberately not migrated

Included: invite-only login (default two users), server-side sessions, separate manual/MT5 journals, notes, balances, daily/weekly/monthly/quarterly UI reports, calendars and decorative farm, read-only device upload tokens and normalized demo trade uploads. Each user's records are scoped on the server. No order endpoints. MT5 USD demo normalization remains in the tested local Python importer.

Not included: hosted candle upload/live charts, paper execution/research engines, trade-plan grouping, chart review snapshots and AI postmortems. Those routes return explicit unavailability. This is not full parity with the local app. No local trades or database passwords are automatically uploaded. Uploads are manual one-shot in this release; do not describe it as automatic cloud sync.

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
