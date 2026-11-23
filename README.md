# Apple FP&A Forecasting Model (Python)
A driver-based financial planning & analysis project for Apple Inc., built for FP&A practice.

## Project Overview
This model uses Apple fiscal year income statement data (FY2022–FY2026) to calculate historical margins, YoY revenue growth, and build Base / Upside / Downside forecast scenarios for FY2027. It also runs sensitivity analysis to measure how revenue growth shocks impact net income.

## Data Source
Data: https://stockanalysis.com/stocks/aapl/financials/income-statement/
Unit: USD Millions

## Files
- `main.py`: Python source code
- `apple_finance.csv`: Raw historical income statement
- `apple_scenarios.csv`: FY2027 three-scenario forecast output
- `apple_sensitivity.csv`: Growth shock sensitivity table
- `apple_fpa_charts.png`: Visualization of revenue trend & gross margin

## How to Run
```bash
pip install pandas numpy matplotlib
python main.py
