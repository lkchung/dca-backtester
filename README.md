# DCA Backtester

A Python-based Dollar-Cost Averaging backtester for US ETFs.
Evaluates strategy performance with IRR, Sharpe, MDD and rolling regime analysis.

## Why I built this
Most DCA discussions online quote returns without showing the underlying assumptions.
I wanted to evaluate the original strategy and extended strategies I designed — 
to evaluate performance using proper metrics like IRR, Sharpe, MDD 
— across different assets and periods, with yfinance numbers while keeping the logic transparent and reproducible.

## How it works
- Base Strategy: buys on the first actual trading day of each month (not calendar day 1)
- -1% Dip Strategy: buys when the ETF (or RSP) drops ≥ 1% — executed next day at open;
  falls back to the third Friday of the month if no dip occurs
- -5% drawdown Strategy: buys when the ETF (or RSP) drops ≥ 5% compare to month start — executed next day at open;
- IRR as primary return metric — accounts for cash flow timing unlike CAGR
- Rolling Sharpe surfaces regime changes hidden by static metrics

## Results (2015–2025, $1,000/month)

### Base Strategy — First Trading Day (Baseline)

| Metric         | SPY     | QQQ     | IWY     |
|----------------|---------|---------|---------|
| Total Invested | 120,000 | 120,000 | 120,000 |
| Final Value    | 257,240 | 335,890 | 338,098 |
| IRR            | 14.6%   | 19.5%   | 19.7%   |
| Volatility     | 17.6%   | 21.8%   | 20.0%   |
| Sharpe         | 0.78    | 0.88    | 0.92    |
| Sortino        | 0.95    | 1.12    | 1.15    |
| MDD            | -32.9%  | -31.4%  | -30.0%  |

**Finding:** ETF selection had more impact on 10-year IRR than any timing overlay tested — 
QQQ/IWY outperformed SPY by ~5pp IRR (19.5-19.7% vs 14.6%) on identical DCA execution. 

### Dip Strategy — Dip Signal + Third-Friday Fallback (QQQ, 2015–2025, Threshold = 1%)

| Strategy & Signal Type | IRR    | Sharpe | MDD     |
|------------------------|--------|--------|---------|
| First Day              | 19.5%  | 0.88   | -31.4%  |
| dip_self + close       | 19.6%  | 0.90   | -31.4%  |
| dip_self + low         | 19.6%  | 0.89   | -31.4%  |
| dip_rsp + close        | 19.6%  | 0.89   | -31.3%  |
| dip_rsp + low          | 19.5%  | 0.89   | -31.3%  |

**Finding:** Within QQQ, Conditional dip strategies show marginal improvement over baseline in Sharpe, IRR and MDD.
Other assets show similar pattern.

### Drawdown Strategy - Drawdown overlay produces no meaningful alpha (QQQ, 2015–2025, Threshold = 5%/7%)

| Strategy & Signal Type        | IRR     | Sharpe | MDD     |
|-------------------------------|---------|--------|---------|
| First Day                     | 19.53%  | 0.88   | -31.4%  |
| drawdown_self -5% + close     | 19.40%  | 0.87   | -30.3%  |
| drawdown_self -7% + close     | 19.47%  | 0.87   | -31.9%  |

**Findings:** Adding a -5%/-7% monthly drawdown overlay on top of Base Strategy improved IRR by < 0.02% across all three ETFs over 10 years.
Two causes: (1) signal triggers only ~15–20 times per decade, statistically diluted by 120 base-layer purchases; (2) IRR improvement reflects beta amplification from deploying more capital, not timing edge.
This raised a cleaner experimental question — isolating signal edge requires equal-capital independent strategies, not overlays. Addressed in W6.

## Base Strategy - Rolling Sharpe Ratio (252-day)

![Rolling Sharpe](assets/rolling_sharpe.png)

| Rolling Sharpe | SPY   | QQQ   | IWY   |
|----------------|-------|-------|-------|
| Mean           | 1.08  | 1.08  | 1.17  |
| Max            | 3.60  | 3.15  | 4.14  |
| Min            | -0.79 | -1.17 | -1.12 |

**Finding:** This rolling Sharpe shows growth (QQQ/IWY) vs SPY leadership mean-reverts over time. Combined with W4 result — same-asset drawdown 
timing added negligible IRR — this suggests cross-asset rotation may carry more signal than within-asset entry timing, worth testing in W6.


## Key Decisions & Tradeoffs

**Incomplete date range > skip rather than truncate**
When a ticker's available data starts after the requested start_date, the backtest skips that ticker entirely rather than running on a shorter window.
Trade-off: fewer results shown, but avoids comparing strategies across unequal time periods.

**Two dip signal variants: `close` vs `low`**
`close` compares prior-day close-to-close return; `low` uses intraday low vs prior close.
Both are valid assumptions depending on whether you execute at open or at close.
Kept both as a `signal_type` parameter rather than hardcoding one.

**`dip_rsp` fallback to `dip_self`**
When RSP data is unavailable, the pipeline falls back to self-signal rather than crashing.
Trade-off: the two signals have different economic assumptions (broad market breadth vs own-price momentum);
fallback is a pipeline safety net, not a strategy equivalence.

**Monthly wallet = 1**
Even when multiple dip signals fire in the same month, only the first is executed.
wallet = 2 would better capture consecutive down days, but increases pipeline complexity and makes cash flow less predictable.
Kept at 1 for MVP scope; can be parameterised later.

**Same-day Base+Drawdown overlap — deduplication, not wallet**
When the base signal (first trading day) and drawdown overlay fire on the same date,
only one buy is executed and the drawdown buy is dropped (`keep="first"`).
This understates total capital deployed on overlap days. Accepted for MVP; correct treatment would allow both executions.


## Limitations & next steps

**Known limitations**
- No transaction costs or slippage
- Sharpe ratio is risk free
- IRR assumes end-of-period liquidation
- Local parquet only; no live data feed
- Drawdown overlay tests capital deployment effect, not signal timing edge; a correct signal-edge test requires equal-capital isolated strategies (W6)

**Planned**
- W5: Gemini API — pass metrics dict, generate narrative investment report with regime analysis
- W6: Independent strategy comparison — equal-capital isolated signals to correctly isolate timing alpha
- W8: GCS + BigQuery — replace local parquet with cloud pipeline
