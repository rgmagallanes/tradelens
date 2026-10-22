# MT5 demo auto-journal

In MT5 Navigator > Indicators, refresh and attach BTC Studio > JournalStudioTrades once on any demo chart. Keep Algo Trading off. Existing quote and margin helpers can remain attached; this is an indicator, not an order EA. In the app choose Journal > Journal source > MT5 demo trades.

Exports every3 seconds to the local common-files studio-trades.json. Backend syncs every2 seconds and journal checks status every5 seconds. First import includes seven days of exits plus older related entries and active positions. Use one exporter on one demo USD hedging account with UTC+0 server. Account changes are refused after the first valid import. No passwords or account holder names are exported. Server/login form a local identity; only its hash is stored by the importer.

Each partial closing deal is a separate closed row. Entry commission/swap/fees are allocated proportionally to closed volume; remainder stays with open volume. Closed net includes reported exit profit/commission/swap/fees plus allocated entry costs. Open floating P/L is excluded. Deposit/withdrawal/credit/account-level fee deals are excluded and counted in sync status. The cumulative ledger starts at zero and is not broker balance or equity. Do not compare return percentages against this ledger.

Recorded trades are immutable through manual trade endpoints. Daily reflections can be edited. Missing/inconsistent histories are flagged; new affected rows omitted, prior reconciled closes retained. Stale/invalid exports do not overwrite journal history. Netting/reversal accounts, non-USD accounts and nonzero server UTC offsets are unsupported in v1. Broker candles only support historical chart reconstruction; imported historical trades have no original entry-time screenshot.

Validation: compare MT5 History against imported deal IDs, lot volumes, execution prices and net costs, including one partial close; refresh/restart to check duplicates. Use demo trades only for this check. Never infer a successful live reconciliation from synthetic fixtures.
