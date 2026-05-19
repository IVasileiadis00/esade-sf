"""
financial_scoring_template.py
-------------------------------
Combines market metrics and fundamental metrics into a draft financial
quality / risk score (0–100) for each portfolio company.

Inputs:
  /data/financial/calculated_metrics/market_metrics_{date}.csv  (from step 2)
  /outputs/scores/financial_metrics_{date}.csv                   (from NB04, contains ROE / D/E / rev growth)

Output:
  /data/financial/calculated_metrics/financial_scores_{date}.csv

Scoring model — five pillars:
  1. Return profile     (25%)  — 1Y return, 3Y return
  2. Risk profile       (25%)  — volatility, max drawdown, Sharpe
  3. Profitability      (25%)  — ROE (from yfinance .info); EBIT margin if available
  4. Balance sheet      (15%)  — D/E ratio; net debt/EBITDA if available
  5. Valuation          (10%)  — placeholder; requires EV/EBITDA or P/E

All sub-scores normalised to 0–100 within the portfolio universe.
Missing inputs are flagged; the pillar weight redistributed or the row marked LOW confidence.

IMPORTANT: This score is a ranking tool within this universe only.
It is NOT investment advice. Human review is required before any portfolio decision.

Dependencies:
  pip install pandas numpy

Run manually only.
"""

import os
import glob
import numpy as np
import pandas as pd
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

METRICS_DIR  = os.path.join(ROOT, "data", "financial", "calculated_metrics")
NB04_DIR     = os.path.join(ROOT, "outputs", "scores")
OUTPUT_DIR   = METRICS_DIR
TODAY        = date.today().isoformat()

# ── Scoring weights (must sum to 1.0) ─────────────────────────────────────────
WEIGHTS = {
    "return":       0.25,
    "risk":         0.25,
    "profitability":0.25,
    "balance_sheet":0.15,
    "valuation":    0.10,
}

# ── Load market metrics ────────────────────────────────────────────────────────
mkt_files = sorted(glob.glob(os.path.join(METRICS_DIR, "market_metrics_*.csv")))
if not mkt_files:
    raise FileNotFoundError(
        f"No market_metrics CSV found in {METRICS_DIR}. "
        "Run calculate_market_metrics_template.py first."
    )
mkt = pd.read_csv(mkt_files[-1])
print(f"Loaded market metrics: {mkt_files[-1]} ({len(mkt)} rows)")

# ── Load NB04 fundamentals (ROE, D/E, revenue growth) ─────────────────────────
nb04_files = sorted(glob.glob(os.path.join(NB04_DIR, "financial_metrics_*.csv")))
if not nb04_files:
    print("WARNING: No NB04 financial metrics file found. Profitability and balance sheet pillars will be MISSING.")
    fund = pd.DataFrame(columns=["ticker", "roe_pct", "debt_to_equity", "revenue_growth_pct"])
else:
    fund = pd.read_csv(nb04_files[-1])
    print(f"Loaded fundamentals: {nb04_files[-1]} ({len(fund)} rows)")

# ── Merge ─────────────────────────────────────────────────────────────────────
df = mkt.merge(
    fund[["ticker", "roe_pct", "debt_to_equity", "revenue_growth_pct"]],
    on="ticker",
    how="left",
)

# ── Normalise helper (higher = better, unless invert=True) ────────────────────
def normalise(series, invert=False):
    """Min-max scale to 0–100. invert=True for metrics where lower is better."""
    s = series.copy().astype(float)
    mn, mx = s.min(), s.max()
    if mx == mn:
        return pd.Series([50.0] * len(s), index=s.index)
    scaled = (s - mn) / (mx - mn) * 100
    return (100 - scaled) if invert else scaled

# ── Pillar 1: Return profile ───────────────────────────────────────────────────
df["return_score"] = normalise(df["return_1y_pct"].fillna(df["return_1y_pct"].mean()))

# ── Pillar 2: Risk profile ─────────────────────────────────────────────────────
vol_score   = normalise(df["annualized_volatility_pct"].fillna(df["annualized_volatility_pct"].mean()), invert=True)
mdd_score   = normalise(df["max_drawdown_pct"].fillna(df["max_drawdown_pct"].mean()), invert=True)
sharpe_score= normalise(df["sharpe_ratio"].fillna(df["sharpe_ratio"].mean()))
df["risk_score"] = (vol_score * 0.33 + mdd_score * 0.33 + sharpe_score * 0.34)

# ── Pillar 3: Profitability ───────────────────────────────────────────────────
roe_available = df["roe_pct"].notna().sum()
rev_available = df["revenue_growth_pct"].notna().sum()
if roe_available > 0 and rev_available > 0:
    roe_score = normalise(df["roe_pct"].fillna(df["roe_pct"].median()))
    rev_score = normalise(df["revenue_growth_pct"].fillna(df["revenue_growth_pct"].median()))
    df["profitability_score"] = (roe_score * 0.6 + rev_score * 0.4)
    df["profitability_data_flag"] = "PARTIAL"
elif roe_available > 0:
    df["profitability_score"] = normalise(df["roe_pct"].fillna(df["roe_pct"].median()))
    df["profitability_data_flag"] = "ROE_ONLY"
else:
    print("WARNING: No profitability data available. Pillar 3 score set to 50 (neutral).")
    df["profitability_score"] = 50.0
    df["profitability_data_flag"] = "MISSING"

# ── Pillar 4: Balance sheet ───────────────────────────────────────────────────
if df["debt_to_equity"].notna().sum() > 0:
    de_score = normalise(df["debt_to_equity"].fillna(df["debt_to_equity"].median()), invert=True)
    df["balance_sheet_score"] = de_score
    df["balance_sheet_data_flag"] = "D/E_ONLY"
else:
    print("WARNING: No balance sheet data available. Pillar 4 score set to 50 (neutral).")
    df["balance_sheet_score"] = 50.0
    df["balance_sheet_data_flag"] = "MISSING"

# ── Pillar 5: Valuation ────────────────────────────────────────────────────────
# Placeholder — EV/EBITDA and P/E not yet collected automatically.
# Set to neutral (50) until data is available.
df["valuation_score"]     = 50.0
df["valuation_data_flag"] = "MISSING — collect EV/EBITDA and P/E manually"

# ── Composite score ────────────────────────────────────────────────────────────
df["financial_quality_score"] = (
    df["return_score"]        * WEIGHTS["return"] +
    df["risk_score"]          * WEIGHTS["risk"] +
    df["profitability_score"] * WEIGHTS["profitability"] +
    df["balance_sheet_score"] * WEIGHTS["balance_sheet"] +
    df["valuation_score"]     * WEIGHTS["valuation"]
).round(2)

# ── Risk flag ─────────────────────────────────────────────────────────────────
def risk_flag(row):
    vol = row.get("annualized_volatility_pct", np.nan)
    sr  = row.get("sharpe_ratio", np.nan)
    de  = row.get("debt_to_equity", np.nan)
    if pd.isna(vol) and pd.isna(sr):
        return "UNKNOWN"
    high = (not pd.isna(vol) and vol > 40) or (not pd.isna(sr) and sr < 0)
    low  = (not pd.isna(vol) and vol < 25) and (not pd.isna(sr) and sr > 0.5)
    if high:
        return "HIGH"
    if low:
        return "LOW"
    return "MEDIUM"

df["financial_risk_flag"] = df.apply(risk_flag, axis=1)

# ── Data confidence ────────────────────────────────────────────────────────────
def confidence(row):
    missing = sum([
        pd.isna(row.get("return_1y_pct")),
        pd.isna(row.get("annualized_volatility_pct")),
        pd.isna(row.get("sharpe_ratio")),
        pd.isna(row.get("roe_pct")),
        pd.isna(row.get("debt_to_equity")),
    ])
    if missing == 0:
        return "HIGH"
    if missing <= 2:
        return "MEDIUM"
    return "LOW"

df["data_confidence"]     = df.apply(confidence, axis=1)
df["calculation_date"]    = TODAY
df["human_review_required"] = True  # always True — score is a ranking tool, not a decision

# ── Output ────────────────────────────────────────────────────────────────────
output_cols = [
    "ticker",
    "return_1y_pct", "return_3y_ann_pct", "return_5y_ann_pct",
    "annualized_volatility_pct", "max_drawdown_pct", "sharpe_ratio", "beta_vs_benchmark",
    "roe_pct", "debt_to_equity", "revenue_growth_pct",
    "return_score", "risk_score", "profitability_score", "balance_sheet_score", "valuation_score",
    "financial_quality_score", "financial_risk_flag", "data_confidence",
    "profitability_data_flag", "balance_sheet_data_flag", "valuation_data_flag",
    "data_sufficiency_flag", "human_review_required", "calculation_date",
]
output_cols = [c for c in output_cols if c in df.columns]
out = df[output_cols]

out_path = os.path.join(OUTPUT_DIR, f"financial_scores_{TODAY}.csv")
out.to_csv(out_path, index=False)
print(f"\nSaved: {out_path}")
print(out[["ticker", "financial_quality_score", "financial_risk_flag", "data_confidence"]].to_string())
print("\nLIMITATIONS:")
print("  - Valuation pillar is MISSING (EV/EBITDA / P/E not yet collected).")
print("  - Banks and insurers (CJ2, SOAN, 2NN, IGQ5) require sector-specific metrics.")
print("  - ROE and D/E from yfinance .info — verify against primary annual report.")
print("  - Score is relative within this universe only. Not investment advice.")
print("  - Human review required before any portfolio decision.")
