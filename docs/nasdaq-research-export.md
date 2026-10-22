# USTEC / US100 historical research export

NasdaqStudioHistory is a read-only demo indicator installed under Indicators → BTC Studio for compatibility with the existing folder. It reads the symbol of the attached chart, accepts names containing USTEC or US100 (including broker suffixes), and has no order, credential, DLL or network APIs.

In MT5, open your actual USTEC/US100 demo chart, refresh Navigator's Indicators, and attach NasdaqStudioHistory. Keep Algo Trading off. Default FromDate is17August2026. The indicator retries history downloads every10seconds, then displays EXPORT COMPLETE with M1/M5/M15/H1 counts. If Max bars is too low, its chart comment explains the needed setting. Downloaded history can have real session gaps; the researcher must check coverage and never fabricate missing candles.

Separate atomic Common Files output: nasdaq-studio-history.json. Includes exact chart symbol, closed/formed OHLC and tick volume, clock/offset, current tick/contract/volume specifications and an observed bid/ask quote. These are not historical spread, commission, margin or funding records. No account login/identity exported. Tick-value currency is the exported account currency; cash sizing is not implied by a point-based research result.

Compilation2026-10-21:0errors/0warnings. Runtime data arrival not yet verified. Existing Bitcoin/gold files and live app behavior are untouched. This prepares data collection, not Nasdaq chart support or a completed Nasdaq strategy test. Next step after receipt: validate exact symbol, UTC basis and chart-price mode, audit complete opening-range sessions, then define Nasdaq tick/cost scenarios before running the three-model experiment. Do not reuse Bitcoin's spread6.40 or its1BTC normalization.
