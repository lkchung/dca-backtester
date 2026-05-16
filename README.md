# DCA Backtester

A Python-based Dollar-Cost Averaging (DCA) backtester for major US ETFs,
evaluating strategy performance across multiple assets and time periods.

## Why I built this
Most DCA discussions online quote returns without showing the underlying assumptions.
I wanted to evaluate the original strategy and extended strategies I designed — 
to evaluate performance using proper metrics like IRR, Sharpe, MDD 
— across different assets and periods, with yfinance numbers while keeping the logic transparent and reproducible.

## How it works
- Buys on the first actual trading day of each month
- IRR (via numpy_financial) as primary return metric — accounts for
  cash flow timing, unlike CAGR which assumes a lump sum
- Risk metrics: MDD, Sharpe, Sortino, Volatility

## Results (2015–2025, $1,000/month)

| Metric         | SPY       | QQQ       | IWY       |
|----------------|-----------|-----------|-----------|
SPY	QQQ	IWY
Total Invested	-120,000.00	-120,000.00	-120,000.00
Final Value	256,240.21	334,890.28	337,098.27
IRR	0.15	0.20	0.20
Volatility	0.18	0.22	0.20
Sharpe	0.78	0.88	0.92
Sortino	0.95	1.12	1.15
MDD	-0.33	-0.31	-0.30

## Rolling Sharpe Ratio

![Rolling Sharpe](assets/rolling_sharpe.png)

| Rolling Sharpe | SPY       | QQQ       | IWY       |
|----------------|-----------|-----------|-----------|
| Mean           |1.10|1.14|1.18
| Min            |-0.79|-1.17|-1.12
| Max            |3.60|3.15|4.14
Max Date: 2018-01-23 (3.60) | 2018-01-23 (3.15)|2018-01-23 (4.14) 
Min Date: 2022-12-28 (-0.79) |min: 2022-12-28 (-1.17) | 2022-12-28 (-1.12)


## Limitations & next steps
**Known limitations**
- No transaction costs or slippage modelled
- IRR assumes end-of-period liquidation — may not realistic for ongoing DCA
- Single data source (local parquet); no live data feed yet

**Planned**
- Strategy B: Conditional buy signal (buy only on down months)
- Gemini API: Auto-generate narrative report from metrics dict
- GCS + BigQuery: Replace local parquet with cloud pipeline

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

## Why rolling Sharpe matters
A static Sharpe ratio hides regime changes.
A strategy may show acceptable long-term performance while experiencing extended periods of weak risk-adjusted returns.
Rolling Sharpe helps reveal:

- unstable periods
- volatility clustering
- prolonged underperformance
- recovery behaviour after drawdowns

Example findings
- Higher-return ETFs did not always produce higher rolling Sharpe
- QQQ generated stronger IRR but experienced longer low-Sharpe periods
- Rolling metrics revealed stability differences hidden by static Sharpe ratios

## Rolling metrics integration

I considered separating rolling analysis into an independent function, but ultimately integrated it into the main run_backtest() pipeline.

Reason:
- both calculations share the same preprocessing logic
- avoids duplicated maintenance
- rolling metrics depend on the same return stream generated during backtest execution

Tradeoff:
- larger main function
- lower synchronization risk between metrics pipelines

## Core Features
- Monthly DCA on first trading day
- Multi-asset comparison
- IRR, Sharpe, Sortino, MDD
- Rolling Sharpe ratio analysis
- Matplotlib visualization

## Current state

- v1: Single-asset script (SPY), linear style
- v2: Refactored into 4 functions, supports multi-asset comparison
- v3:
rolling Sharpe analysis
matplotlib visualization
validation improvements

## Refactor notes (v3)
Date Validation
Rolling Sharpe ratio calculation
Regime stability analysis
Automatic detection of:
max rolling Sharpe period
min rolling Sharpe period
Time-series visualization using matplotlib


