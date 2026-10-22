# Reversed-entry experiment v7

**Result: reversal did not establish positive modeled expectancy. All8 runs lost money. Exploratory / UNPROVEN.**

Raw EMA trend-reclaim signals are generated identically. Forward takes the original direction; reverse takes the opposite direction, swaps stop/target boundaries and translates bid/ask triggers to preserve the underlying bid boundaries. New eligibility and risk-based sizes are calculated for each direction. Entry must occur at next contiguous M1 open. No selecting only losing trades after the fact.

| Direction | Spread/BTC | Window | Wins / trades | Net modeled P/L | Closed-equity drawdown |
|---|---:|---|---:|---:|---:|
| Original | $6.40 | Recent7 days | 4 / 7 | $-1.79 | $14.23 |
| Original | $6.40 | Earlier3 days | 2 / 7 | $-16.86 | $19.51 |
| Original | $12.80 | Recent7 days | 4 / 7 | $-1.99 | $14.43 |
| Original | $12.80 | Earlier3 days | 1 / 5 | $-15.29 | $15.29 |
| Reversed | $6.40 | Recent7 days | 3 / 8 | $-6.86 | $8.71 |
| Reversed | $6.40 | Earlier3 days | 6 / 11 | $-6.34 | $11.84 |
| Reversed | $12.80 | Recent7 days | 5 / 10 | $-1.48 | $8.98 |
| Reversed | $12.80 | Earlier3 days | 3 / 8 | $-15.01 | $15.19 |

## What this means

At normal modeled spread, reversing worsened recent-week P/L from-$1.79 to-$6.86 and improved the earlier period from-$16.86 to-$6.34, but neither was profitable. Doubled-spread reverse results were-$1.48 recently and-$15.01 earlier. All runs hit a risk pause. The raw signals are identical, but net-R gates, stop distances, lot rounding, holding times, overlap and pause timing change eligible trades. Reversed winning percentage is not simply100% minus original winning percentage.

For identical bid endpoints and equal volume, gross directional P/L flips sign but spread/slippage are still paid. With fixed total per-trade cost C, reversed net=-original net-2C. A strategy that loses only through transaction costs can lose in both directions. A systematically wrong before-cost forecast might have an inverse edge; that must be demonstrated on unseen data rather than inferred from a few losing trades. These outputs do not demonstrate it.

## Controls and limitations

Same source/windows as v4/v6, initial1000, default0.5%/$5 risk budget, original0.5-net-R minimum, no target caps, modeled zero commission, fixed6.40/12.80 spread and adverse5/BTC/fill slippage. Historical quotes, execution latency, margin and news context are unavailable. Earlier and recent windows were already viewed; repeated candidate search causes selection bias. Stop-first ambiguous candle handling, gap uncertainty and end-of-data exclusions retained. No live paper or broker changes.

45 backend tests passed, including bid/ask trigger-preserving reversal, long/short restoration and the cost identity. Original-direction results reproduce all corresponding v6 original-target runs. Raw signal counts match for each paired replay; shared eligible signals have opposite trade directions. Approved v1 file integrity passed.

Source SHA256: `c94477e213d73f582a1231c5e3771ab0e10ad40dd79c73f4baa01db16d0cd6e3`

`strategy/reversed-entry-research-v7.md` SHA256: `a44d37a018863228da9d172ccd7adc9864bec7cf1b3d6156a1aa0650eb4e2014`

`strategy/high-win-rate-screen-v4.md` SHA256: `f1399c8b666528aa482a0cf9061af088a4e4d701a5f65eeb47c8ea752ce5ebb0`

`backend/high_win_screen.py` SHA256: `3a7909d526a15118448382368efd166de585f1343bba3bbb6ccc819ebe346b30`

Specification: `strategy/reversed-entry-research-v7.md`; full logs: `research/reversed-entries-2026-10-19.json`. Reproduce via `python -m backend.run_reversal --input research/exness-history-v2-2026-10-19.json --output /tmp/reversal.json`.
