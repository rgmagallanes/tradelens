# Earlier take-profit comparison v6

**No profitable outcome found among the16 fixed scenario/window runs. Exploratory / UNPROVEN.**

The same v4 EMA trend-reclaim signals,0.5%/$5 sizing, stops,30min time exits and risk pauses were replayed. The only intervention was to cap the original target at approximately0.5,0.75 or1.0 net R. An original target already closer than a cap stays unchanged. R includes modeled stop-exit slippage; target prices account for adverse target slippage. No cap can make an originally ineligible entry qualify. No stop moved to breakeven, trailing stop or live trade changes were made.

| Target | Spread/BTC | Window | Wins / trades | Net modeled P/L | Closed-equity drawdown |
|---|---:|---|---:|---:|---:|
| Original | $6.40 | Recent7 days | 4 / 7 | $-1.79 | $14.23 |
| Original | $6.40 | Earlier3 days | 2 / 7 | $-16.86 | $19.51 |
| Original | $12.80 | Recent7 days | 4 / 7 | $-1.99 | $14.43 |
| Original | $12.80 | Earlier3 days | 1 / 5 | $-15.29 | $15.29 |
| Cap 0.5R | $6.40 | Recent7 days | 4 / 7 | $-5.02 | $14.23 |
| Cap 0.5R | $6.40 | Earlier3 days | 3 / 8 | $-15.68 | $18.01 |
| Cap 0.5R | $12.80 | Recent7 days | 4 / 7 | $-5.22 | $14.43 |
| Cap 0.5R | $12.80 | Earlier3 days | 2 / 7 | $-18.41 | $18.41 |
| Cap 0.75R | $6.40 | Recent7 days | 4 / 7 | $-2.28 | $14.23 |
| Cap 0.75R | $6.40 | Earlier3 days | 2 / 7 | $-16.86 | $19.51 |
| Cap 0.75R | $12.80 | Recent7 days | 4 / 7 | $-2.47 | $14.43 |
| Cap 0.75R | $12.80 | Earlier3 days | 1 / 5 | $-15.29 | $15.29 |
| Cap 1.0R | $6.40 | Recent7 days | 4 / 7 | $-1.79 | $14.23 |
| Cap 1.0R | $6.40 | Earlier3 days | 2 / 7 | $-16.86 | $19.51 |
| Cap 1.0R | $12.80 | Recent7 days | 4 / 7 | $-1.99 | $14.43 |
| Cap 1.0R | $12.80 | Earlier3 days | 1 / 5 | $-15.29 | $15.29 |

## Findings

At normal modeled spread, earlier0.5R exits reduced recent-week net performance from-$1.79 to-$5.02, with the same4 wins out of7 trades. The earlier comparison window improved slightly from-$16.86 to-$15.68 and3 wins out of8, but remained negative. Under doubled spread the earlier0.5R result deteriorated to-$18.41. The0.75R cap lost$2.28 in the recent week and$16.86 earlier. The1R cap made no difference to these realized totals because original targets were already closer or another exit occurred first.

All runs hit a risk pause. Different exit times can alter overlapping entry eligibility and subsequent pause timing; therefore these are chronological policy comparisons, not simply editing P/L on a fixed trade list. None supports the claim that adjusting take profit alone makes the system profitable. The same reused history has been searched repeatedly, so no clean validation claim is made.

## Assumptions and verification

Constant modeled spreads$6.40/$12.80 perBTC; adverse$5/BTC/fill slippage; zero modeled commission; bid OHLC and modeled ask short exits. Historical execution, margin, latency and news review unverified. Stop-first ambiguous bars, next-open entries, gap handling and end-of-data exclusions retained. Full JSON logs retain all trade/cost/risk/gap/open-position records; no favorable samples omitted.

44 backend tests passed, including long/short net-cost target rounding, unchanged shared-entry stop/size, preserving nearer original targets, next-open timing and prior risk controls. Original-target results reproduce all corresponding0.5% v5 outputs exactly. Approved v1 file integrity passed and live records were not changed.

Source SHA256: `c94477e213d73f582a1231c5e3771ab0e10ad40dd79c73f4baa01db16d0cd6e3`

`strategy/take-profit-research-v6.md` SHA256: `bc29b8ac327cfb2f3da1431b644d544946bc02b2f8043571fe8245cee5847653`

`strategy/high-win-rate-screen-v4.md` SHA256: `f1399c8b666528aa482a0cf9061af088a4e4d701a5f65eeb47c8ea752ce5ebb0`

`backend/high_win_screen.py` SHA256: `39de8c1ca55b3eb0f2091a01c46d8538f81a8e4da2e02e7ed115ae4ef20f6d6e`

Specification: `strategy/take-profit-research-v6.md`; full output: `research/take-profit-comparison-2026-10-19.json`. Reproduce with `python -m backend.run_target_comparison --input research/exness-history-v2-2026-10-19.json --output /tmp/target-comparison.json`.
