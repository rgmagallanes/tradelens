# Automatic lower-timeframe research — seven-day replay

**UNPROVEN. Candle-modeled research; historical margin and executable fills are unverified.**

Window: 2026-10-12 12:00 to 2026-10-19 12:00, MT5 broker-server clock. The lower candidate uses 10,068 completed M1 bars. Twelve expected minute bars are missing in one gap on 18 October. Earlier bars supply warmup.

| Candidate | Assumed spread per BTC | Closed trades | Net modeled P/L | Realized drawdown | Risk pause |
|---|---:|---:|---:|---:|---|
| M15 levels / M5 entry / H1 EMA context | $6.40 | 0 | $0.00 | $0.00 | No |
| M15 levels / M5 entry / H1 EMA context | $12.80 | 0 | $0.00 | $0.00 | No |
| M5 levels / M1 entry / M15 EMA context | $6.40 | 3 | $-6.55 | $6.55 | Yes |
| M5 levels / M1 entry / M15 EMA context | $12.80 | 3 | $-6.11 | $6.11 | Yes |

The lower candidate closed three losing trades, then paused for the rest of this replay under the preregistered three-loss rule. All three occurred on 13 October. The final two-day validation segment had no trades because the candidate was paused; that is not evidence of an absence of opportunities or independent validation. The reference candidate generated 80 registrations and no eligible fills. It is a new automatic-level/EMA candidate, not the frozen manual v1 baseline.

## Lower candidate trades at $6.40 modeled spread

| Entry, broker time | Direction | Volume, lots | Exit | Net P/L |
|---|---|---:|---|---:|
| 2026-10-13 02:48 | Long | 0.05 | TIME | $-1.41 |
| 2026-10-13 03:35 | Long | 0.01 | TIME | $-0.31 |
| 2026-10-13 05:17 | Long | 0.06 | STOP | $-4.83 |

At $6.40 spread the modeled spread plus fixed slippage costs totaled $1.97; at doubled spread $2.28. Costs are included in P/L, not deducted twice. Doubled spread produced a slightly smaller total loss because risk-based lot sizing rounded volumes down; it did not improve the price of any fill. There were no ambiguous stop/target bars and no open positions at the end. Realized drawdown excludes unrealized intratrade excursions.

## Method and limitations

- Automatic two-reaction pivot levels and targets use completed historical candles only. Registration cannot qualify an earlier breakout.
- M1 entries use the next contiguous bar open following confirmation; 2 net R, $5/0.5% risk budget and 30-minute time exit retained.
- Constant $6.40/$12.80 spreads and $5 adverse slippage per BTC per fill are assumptions, not historical measured execution. Bid OHLC cannot establish quote latency or broker fill quality.
- USD0 commission, current contract/lot increments and tick size are modeled assumptions. Historical margin availability is not verified.
- The first five days are exploratory and final two days were designated validation before this candidate run, but the history was recently viewed. This is not pristine out-of-sample evidence.
- News context is assumed clear; no historical manual news decisions are available.
- One missing M5 candle / twelve missing M1 candles occur in the same gap. Pending setups are cancelled at gaps; no gap crossed an open position in these runs.
- Three trades from one week cannot establish profitability. These results do not support activating this candidate for real funds.

## Reproducibility

Source SHA256: `c94477e213d73f582a1231c5e3771ab0e10ad40dd79c73f4baa01db16d0cd6e3`
Research specification SHA256: `5b2002ebfb584d14697d66fd18f18d85a6b885b3bc091183cdc2274f05293503`

Frozen source: `exness-history-v2-2026-10-19.json`; full result: `automatic-lower-timeframe-week-2026-10-19.json`. Research rules: `strategy/lower-timeframe-research-v2.md`. Reproduce with the backend.run_auto_research module. All 32 backend tests passed after the run. No approved-v1 parameters, live paper settings, levels or positions were changed.
