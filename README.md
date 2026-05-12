# DCA Backtester

A Python-based Dollar-Cost Averaging (DCA) backtester for major US ETFs,
evaluating strategy performance across multiple assets and time periods.

## Why I built this

Most DCA discussions online quote returns without showing 
the underlying assumptions. I wanted to 
evaluate the original strategy and and extended strategies I designed — 
to evaluate performance using proper metrics  — IRR, Sharpe, MDD 
— across different assets and periods, with yfinance numbers that I could 
verify myself.

## How it works

- Buys on the first actual trading day of each month
- IRR (via numpy_financial) as primary return metric — accounts for
  cash flow timing, unlike CAGR which assumes a lump sum
- Risk metrics: MDD, Sharpe, Sortino, Volatility

## Key decisions & tradeoffs

**First trading day detection**
Used `groupby(pd.Grouper(freq="MS")).nth(0)` instead of `.first()` or
`resample()`. Both alternatives return the calendar start of the month,
not the actual first trading day — which matters when markets are closed
on the 1st.

**Strategy return calculation**
Deducted monthly cashflow from daily return:
```python
strategy_return = (port_value - port_value.shift(1) - cashflow_series) 
                  / port_value.shift(1)
```
Without this adjustment, the monthly investment inflow inflates the
return figure — making the strategy look better than it is on buy days.

## Results (2022–2025, $1,000/month)

| Metric         | SPY       | QQQ       | IWY       |
|----------------|-----------|-----------|-----------|
| Total Invested | 36,000    | 36,000    | 36,000    |
| Final Value    | 47,018    | 50,816    | 53,066    |
| IRR            | 21%       | 27%       | 30%       |
| Volatility     | 18%       | 24%       | 22%       |
| Sharpe         | 0.56      | 0.49      | 0.58      |
| Sortino        | 0.80      | 0.71      | 0.84      |
| MDD            | -13%      | -15%      | -14%      |

## Current state

- v1: Single-asset script (SPY), linear style
- v2: Refactored into 4 functions, supports multi-asset comparison

## Limitations & next steps

**Known limitations**
- No input validation — passing an invalid date range fails silently
- No transaction costs or slippage modelled
- IRR assumes end-of-period liquidation — not realistic for ongoing DCA
- Single data source (local parquet); no live data feed yet

**Planned**
- Strategy B: Conditional buy signal (buy only on down months)
- Gemini API: Auto-generate narrative report from metrics dict
- GCS + BigQuery: Replace local parquet with cloud pipeline