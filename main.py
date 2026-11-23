"""
Apple FP&A Forecasting Project  (driver-based, scenario model)
------------------------------------------------------------------
Data: Apple 10-K income statements, FY2022 - FY2026 (fiscal year ends late Sept)
Data source: https://stockanalysis.com/stocks/aapl/financials/income‑statement/
Unit: USD millions

Method (this is how real FP&A teams forecast, not naive linear regression):
1. Compute historical gross margin / net margin / YoY revenue growth
2. Use trailing-3-year average revenue growth as the BASE driver
3. Build Base / Upside (+2pp) / Downside (-2pp) scenarios for FY2027
4. Sensitivity table: growth shock -> revenue & net income
5. Charts: revenue trend + scenarios, margin trend

Outputs: apple_fpa_charts.png, apple_scenarios.csv, apple_sensitivity.csv
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV_PATH = "apple_finance.csv"
FORECAST_YEAR = 2027
SHOCK_PP = 0.02          # +/- 2 percentage points for upside / downside

df = pd.read_csv(CSV_PATH)
df["Gross_Margin"] = (df["Revenue"] - df["COGS"]) / df["Revenue"]
df["Net_Margin"] = df["Net_Income"] / df["Revenue"]
df["Revenue_Growth_YoY"] = df["Revenue"].pct_change()
df["Net_Income_Growth_YoY"] = df["Net_Income"].pct_change()

print("===== Apple Historical Financial Summary (USD millions) =====")
print(df.round(4).to_string(index=False))

# ---------- drivers ----------
last = df.iloc[-1]
base_growth = df["Revenue_Growth_YoY"].tail(3).mean()    # trailing 3-yr avg growth
base_margin = df["Net_Margin"].tail(3).mean()            # trailing 3-yr avg net margin
capex_note = "OpEx ratio kept flat at FY2026 level"

print(f"\n===== Drivers =====")
print(f"Trailing 3-yr avg revenue growth : {base_growth:.2%}")
print(f"Trailing 3-yr avg net margin     : {base_margin:.2%}")
print(f"FY2026 revenue                   : ${last['Revenue']:,.0f}M")
print(f"FY2026 net income                : ${last['Net_Income']:,.0f}M")

# ---------- scenarios ----------
scen = [
    ("Downside", base_growth - SHOCK_PP),
    ("Base",     base_growth),
    ("Upside",   base_growth + SHOCK_PP),
]
rows = []
for name, g in scen:
    rev = last["Revenue"] * (1 + g)
    # scenario margin: downside also compresses margin slightly
    margin = base_margin + (0.01 if name == "Upside" else (-0.01 if name == "Downside" else 0.0))
    net = rev * margin
    rows.append({"Scenario": name, "Revenue_Growth": g, "Revenue": rev,
                 "Net_Margin": margin, "Net_Income": net,
                 "Revenue_vs_Base": np.nan, "Net_vs_Base": np.nan})

scen_df = pd.DataFrame(rows)
base_rev = scen_df.loc[scen_df["Scenario"] == "Base", "Revenue"].iloc[0]
base_net = scen_df.loc[scen_df["Scenario"] == "Base", "Net_Income"].iloc[0]
scen_df["Revenue_vs_Base"] = scen_df["Revenue"] - base_rev
scen_df["Net_vs_Base"] = scen_df["Net_Income"] - base_net

print(f"\n===== FY{FORECAST_YEAR} Scenario Forecast =====")
show = scen_df.copy()
show["Revenue_Growth"] = show["Revenue_Growth"].map("{:.2%}".format)
show["Net_Margin"] = show["Net_Margin"].map("{:.1%}".format)
show["Revenue"] = show["Revenue"].map(lambda v: f"${v:,.0f}M")
show["Net_Income"] = show["Net_Income"].map(lambda v: f"${v:,.0f}M")
show["Revenue_vs_Base"] = show["Revenue_vs_Base"].map(lambda v: f"{v:+,.0f}")
show["Net_vs_Base"] = show["Net_vs_Base"].map(lambda v: f"{v:+,.0f}")
print(show.to_string(index=False))
scen_df.to_csv("apple_scenarios.csv", index=False)

# ---------- sensitivity table ----------
print(f"\n===== Sensitivity: revenue growth shock vs net income =====")
sens_rows = []
for shock in [-0.06, -0.04, -0.02, 0.0, 0.02, 0.04, 0.06]:
    g = base_growth + shock
    rev = last["Revenue"] * (1 + g)
    net = rev * base_margin
    sens_rows.append({"Growth_Shock": shock, "FY27_Growth": g,
                      "Revenue": rev, "Net_Income": net})
    print(f"  {shock:+.0%} -> growth {g:.1%} | Revenue ${rev:,.0f}M | Net ${net:,.0f}M")
pd.DataFrame(sens_rows).to_csv("apple_sensitivity.csv", index=False)

# ---------- charts ----------
plt.rcParams["figure.figsize"] = (14, 5.5)
fig, axes = plt.subplots(1, 2)

ax = axes[0]
ax.plot(df["Year"], df["Revenue"] / 1000, marker="o", linewidth=2,
        label="Historical Revenue")
colors = {"Downside": "gray", "Base": "crimson", "Upside": "seagreen"}
for _, r in scen_df.iterrows():
    ax.scatter(FORECAST_YEAR, r["Revenue"] / 1000, s=110, zorder=5,
               color=colors[r["Scenario"]],
               label=f"FY{FORECAST_YEAR} {r['Scenario']}")
    ax.annotate(f"{r['Revenue']/1000:.0f}", (FORECAST_YEAR, r["Revenue"] / 1000),
                textcoords="offset points", xytext=(-8, 8), fontsize=9,
                ha="right", va="bottom")
ax.set_title(f"Apple Revenue Trend & FY{FORECAST_YEAR} Scenario Forecast")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("Revenue (USD billions)")
ax.set_xticks(list(df["Year"]) + [FORECAST_YEAR])
ax.set_xlim(df["Year"].min() - 0.4, FORECAST_YEAR + 0.5)
ax.legend(fontsize=8, loc="upper left")
ax.grid(alpha=0.3)

ax = axes[1]
ax.plot(df["Year"], df["Gross_Margin"] * 100, marker="o", color="seagreen",
        label="Gross Margin %")
ax.plot(df["Year"], df["Net_Margin"] * 100, marker="s", color="steelblue",
        label="Net Margin %")
ax.set_title("Apple Gross Margin vs Net Margin")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("%")
ax.set_xticks(df["Year"])
ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("apple_fpa_charts.png", dpi=150)
print("\nSaved: apple_fpa_charts.png / apple_scenarios.csv / apple_sensitivity.csv")
