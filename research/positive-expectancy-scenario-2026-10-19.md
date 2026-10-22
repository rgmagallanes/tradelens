# A positive-expectancy scenario to validate

**Hypothetical arithmetic, not an achieved backtest, forecast or trade recommendation.**

Assume BTC bid100000,0.02lot=0.02BTC, virtual balance1000. Stop bid99800 ($200 price move); target bid100400 ($400 move). Notional2000 and illustrative margin4 only if500:1 applies. No live-price entry proposed. Numbers are illustrative, not tuned to historical prices.

Modeled round-trip cost: spread6.40/BTC plus5/BTC adverse slippage each side, zero commission. Total0.328/trade. Target gross8 becomes net7.672; stop gross4 becomes net4.328 loss. Actual gaps, funding or time exits can invalidate these fixed-payoff assumptions.

| Assumed win rate | Expected net/trade | Conditional total over100 such trades |
|---|---:|---:|---:|
| 30% | $-0.728 | $-72.80 |
| 35% | $-0.128 | $-12.80 |
| 40% | $0.472 | $47.20 |
| 45% | $1.072 | $107.20 |
| 50% | $1.672 | $167.20 |

At45% wins:45*7.672 minus55*4.328 =107.20. Accounting break-even win fraction36.07%. At doubled spread, same assumed45% fixed-payoff distribution gives94.40, with37.13% break-even. These are conditional arithmetic, not performance evidence. No ability to achieve those future trades/win rates/payoffs is established.

## What differs from our actual results

Original-direction, normal-spread9-reset-window audit: 68 selected closed trades; cost-added-back P/L$11.52; modeled costs$61.50; net$-49.98. Just reaching accounting break-even with the same selected gross outcomes would require a 81.3% reduction in modeled costs. Actual costs cannot be assumed that much lower. This is not a zero-cost policy rerun: cost eligibility, holding and pauses could change. Some earlier samples were negative before cost addback too.

## Validation plan

1. Diagnose all raw signals throughout the full period independently of account pauses: before-cost forward price movement, favorable/adverse excursion and time to thresholds. Clearly distinguish overlapping diagnostic signals from executable trades.
2. Obtain historical or recorded bid/ask to replace constant costs, preserving actual server/account provenance and latency/gap limitations.
3. Freeze one entry hypothesis and stop/target method before reading additional evaluation data; treat existing history as development data.
4. Evaluate unseen history, then forward demo. Measure net expectancy, costs, drawdown and pauses. Reject if returns do not persist instead of rescuing results with leverage or smaller targets.

The scenario requires a combination like45% net-winning outcomes and average winning payout about1.77 times average losing payout after assumed costs. We have not demonstrated that combination. Increased leverage does not create it. No real or live-paper settings were changed.
