# Tick-volume scalping comparison

EXPLORATORY / UNPROVEN

| Volume filter | News | Spread | Trades | Win rate | Net P/L | Closed-equity DD |
|---|---|---|---:|---:|---:|---:|
| Off | False | 6.4 | 84 | 34.5% | $-99.83 | $101.92 |
| 1.5 | False | 6.4 | 4 | 25.0% | $-9.50 | $14.18 |
| Off | False | 12.8 | 72 | 33.3% | $-92.90 | $100.84 |
| 1.5 | False | 12.8 | 4 | 25.0% | $-9.57 | $14.18 |
| Off | True | 6.4 | 84 | 34.5% | $-99.83 | $101.92 |
| 1.5 | True | 6.4 | 4 | 25.0% | $-9.50 | $14.18 |
| Off | True | 12.8 | 72 | 33.3% | $-92.90 | $100.84 |
| 1.5 | True | 12.8 | 4 | 25.0% | $-9.57 | $14.18 |

Research only. Tick volume measures quote activity, not institutional identities. Previously viewed data; costs are modeled and funding/margin unverified. No live activation. See JSON for source hashes, parity audit and complete trade/risk records.

## Findings and verification

The 1.5× filter did not establish a profitable edge. At normal modeled spread it reduced closed trades from 84 to 4, with one win and three losses, net −$9.50. Double spread produced −$9.57. The smaller total loss reflects far fewer trades; it is not evidence of better expectancy. Four trades are too few for a reliable performance conclusion. News ON/OFF had identical executed trade records.

Volume-filtered runs processed the entire requested 61-day interval without an account drawdown stop. Baselines reached the permanent drawdown stop and then processed later candles diagnostically without new entries. No run ended with an open or uncertain position. Missing-candle gaps remain in source history and retain the existing continuity rules.

Source parity passed for 88,089 M1 and 17,622 M5 candles, including warmup. All 87,809 M1 candles in the volume audit interval (including 20-minute warmup) had positive integer tick counts; none had nonzero real volume. Every baseline trade record exactly reproduced the saved v12 result. Every filtered entry's tick-volume ratio was independently recomputed from its preceding 20 bars and its next-minute entry timestamp checked. All 66 backend tests passed.

No live or paper configuration was changed. No threshold sweep was performed. Research status: UNPROVEN / NOT SUITABLE FOR ACTIVATION.
