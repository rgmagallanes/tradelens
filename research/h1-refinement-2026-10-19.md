# H1 refinement review — v11

**Decision: retain the original v10 baseline for further validation. Neither tested refinement improved it. UNPROVEN; no live changes.**

The two refinements were specified before the run: EMA50 direction/slope at signal and entry, then that filter plus skipping a signal candle with range greater than2 × prior-bar ATR. Channel lengths,2 × ATR stop,0.5% risk, minimum lot size, costs and loss pauses were unchanged. No post-result threshold adjustment or risk-control relaxation.

## All twelve fixed scenarios

P/L below includes assumed spread/slippage but excludes unverified historical swaps.

| Virtual balance | Profile | Spread/BTC | Closed trades | Wins | P/L excluding swaps | Realized drawdown |
|---|---|---:|---:|---:|---:|---:|
| $1,000 | Original H1 | $6.40 | 4 | 1 | $+100.46 | $15.76 |
| $1,000 | Original H1 | $12.80 | 4 | 1 | $+100.39 | $15.76 |
| $1,000 | H1 + EMA50 | $6.40 | 4 | 1 | $+100.46 | $15.76 |
| $1,000 | H1 + EMA50 | $12.80 | 4 | 1 | $+100.39 | $15.76 |
| $1,000 | H1 + EMA50 + range check | $6.40 | 4 | 1 | $-10.09 | $10.09 |
| $1,000 | H1 + EMA50 + range check | $12.80 | 4 | 1 | $-10.22 | $10.22 |
| $10,000 | Original H1 | $6.40 | 4 | 1 | $+1,190.04 | $88.36 |
| $10,000 | Original H1 | $12.80 | 4 | 1 | $+1,188.76 | $88.93 |
| $10,000 | H1 + EMA50 | $6.40 | 4 | 1 | $+1,190.04 | $88.36 |
| $10,000 | H1 + EMA50 | $12.80 | 4 | 1 | $+1,188.76 | $88.93 |
| $10,000 | H1 + EMA50 + range check | $6.40 | 4 | 1 | $-52.03 | $138.86 |
| $10,000 | H1 + EMA50 + range check | $12.80 | 4 | 1 | $-52.22 | $138.86 |

## What the refinements taught us

EMA50 rejected four $1000-account signals that were not executable under minimum-lot sizing anyway, so all actually executed trade logs matched the baseline. It added complexity without demonstrated performance benefit on this period. That is not a general claim that EMA filters cannot help.

The range check removed the large initial winning breakout. The $1000 case then lost$10.09 at normal spread ($10.22 at doubled spread). Its single small winner earned$1.49; loss pauses did not trigger in that normal-spread case, so it evaluated the full period with54 size rejections. The separately initialized $10000 case also became negative. These adverse outcomes are retained rather than tuning the range threshold around the known winning trade.

## Concentration and sizing

The original $1000 result is+$100.46 before swaps. Simply subtracting its largest winning trade leaves-$15.76. This is an accounting concentration diagnostic, not a strategy rerun: removing a historical win would also change subsequent equity, sizing and eligibility. The fact remains that one outcome supplies all positive P/L. Four closes do not establish a stable edge.
The original $1000 scenario rejected21 signals under the unchanged0.01 lot/0.5% risk constraint. Minimum equity required for those hypothetical entries ranged from$1,377.52 to$2,965.28. This is not a recommendation to add funds. More leverage reduces margin, but does not shrink the stop-loss dollar amount for the minimum lot.
The original policy spent446 H1 evaluation bars before or through its loss pause and1018 bars risk-paused. The permanent pause was not removed to inflate activity. No new rule is activated to automatically resume it.

## Funding sensitivity remains a proxy

For the original $1000 normal-spread closed trades, conservative held-duration exposure is0.05 lot-days. Applying invented accounting costs of$10/$30 per lot per24h subtracts$0.50/$1.50, leaving+$99.96/+$98.96. These are not Exness quotes or actual swap calculations; weekend/triple-day schedules, changing rates, credits, swap-free history and equity feedback are not simulated. They do not establish verified net profitability.

[Exness swap-free status documentation](https://get.exness.help/hc/en-us/articles/4402341895570-Swap-free-status) lists cryptocurrencies under eligible instruments but says status can change and is checked in Personal Area > Exness benefits > Trading conditions > Swap-Free. No personal account status has been inspected, so actual historical eligibility remains unknown.

## Retained candidate and next gate

Keep v10 intact: prior 20 completed-H1 breakout, next-open entry,2 × ATR protective stop, opposite prior 10-bar completed-close exit,0.5% risk and existing pauses. Do not add the tested EMA/range filters as a claimed improvement. Verify costs/funding, test a separate unseen period, and forward-observe on demo before any activation decision. The same Aug–Oct data have already been inspected across candidates, so none of these refinements constitutes clean out-of-sample evidence.

## Verification

60 backend tests passed. New tests cover EMA warmup/direction/continuity, range equality against prior ATR, rechecking trend before entry without reading the future entry candle, and explicit accounting-only concentration/carry diagnostics. Baseline per-trade logs reproduce all four v10 account/cost scenarios exactly. EMA50 actual trade logs match corresponding baselines; no open or uncertain end positions in any of the 12 scenarios. Approved v1 frozen integrity passed. No live configuration or trading records mutated.

Source SHA256: `a3846f5fc2f22a156cfff52f5695c56ebdac0bec5237cabb9e3eb82be238e50e`

`strategy/h1-refinement-research-v11.md` SHA256: `1d6e5d8d114fcb7c66c10257d9bd0426e8081a09631548d3d3f6e0ffa2639ec3`

`strategy/h1-channel-research-v10.md` SHA256: `782cde7f1b286aa99436d4b00e75c22a86025909b3f0d31bce4ab13b475aa3cf`

`backend/h1_channel_research.py` SHA256: `1f6aa6304789710b43e47ea4df77ccad1d791b0e4b37226ee49b68195d539216`

Full output: `research/h1-refinement-2026-10-19.json`. Fixed spec: `strategy/h1-refinement-research-v11.md`. Decision record: `strategy/h1-research-decision-v11.json`. Reproduce via `python -m backend.run_h1_refinement --input research/exness-history-2months-2026-10-19.json --output /tmp/h1-refinement.json`.
