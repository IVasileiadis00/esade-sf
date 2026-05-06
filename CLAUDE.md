# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

**ESADE MSc Finance — Final Group Assignment**
Build an AI-agent research pipeline for sustainable portfolio construction. The output is a 15–25 stock long-only equity portfolio with a full methodology report (5,000–6,500 words) and live demo.

**Deadline:** Friday 22 May 2026, 18:15–20:15 (final presentation + Q&A)
**Assessment:** Written report 60%, Presentation + Demo + Q&A 40%

This is an academic prototype — not a regulated investment product or financial advice.

## Running the Project

**First-time setup (one-time only):**
1. Install Python: `winget install Python.Python.3.11` in a terminal, then restart the terminal
2. In the project folder, double-click `setup.bat` — this installs all packages and creates the Jupyter kernel
3. Double-click `launch_jupyter.bat` to open Jupyter Notebook in your browser

**Normal usage:** Double-click `launch_jupyter.bat`, then run notebooks in order (00 → 01 → 01b → 02 → 03 → 04 → 06 → 07 → 08 → 09 → 10 → 05).

**Notebooks (run in this order):**
| Notebook | Agent # | What it does |
|----------|---------|-------------|
| `notebooks/00_mandate.ipynb` | Agent 1 — Mandate | Defines investment thesis, scoring weights, exclusion rules; saves mandate.json |
| `notebooks/01_data_ingestion.ipynb` | Agent 2 — Data Ingestion | Loads 4 CSVs, downloads prices via yfinance, saves master dataset |
| `notebooks/01b_data_quality.ipynb` | Agent 3 — Data Quality | Missing-value audit, outlier detection, data dictionary, taxonomy note |
| `notebooks/02_financial_analysis.ipynb` | Agent 10 — Financial Analysis | Calculates returns, volatility, Sharpe ratio, drawdown |
| `notebooks/03_esg_scoring.ipynb` | Agents 5 & 6 — ESG + Climate | Builds E, S, G and combined ESG scores (0–100), calculates WACI |
| `notebooks/06_document_intelligence.ipynb` | Agent 4 — Document Intelligence | Imports Claude Projects RAG extractions from sustainability report PDFs |
| `notebooks/07_biodiversity.ipynb` | Agent 7 — Biodiversity | Nature-risk proxy scores (ENCORE + WRI Aqueduct) per company |
| `notebooks/08_eu_regulation.ipynb` | Agent 8 — EU Regulation | EU Taxonomy, SFDR Article 8 compliance, PAI indicators |
| `notebooks/09_greenwashing.ipynb` | Agent 9 — Greenwashing | Imports 8-Test JSON from Claude Projects, scores and applies exclusions |
| `notebooks/04_portfolio_construction.ipynb` | Agent 11 — Portfolio Construction | Applies exclusions, ranks, selects 20 holdings with weights |
| `notebooks/10_human_review.ipynb` | Agent 12 — Human Review | Override decision log, AI Use Statement |
| `notebooks/05_reporting.ipynb` | Agent 13 — Reporting | Generates charts and factsheet metrics |
| `notebooks/05_reporting.ipynb` | Reporting | Generates charts and factsheet metrics |

**Output files land in:**
- `outputs/scores/` — master dataset, ESG scores, financial metrics
- `outputs/portfolio/` — final portfolio, exclusion log, universe scores
- `outputs/reports/` — charts (PNG) ready for presentation slides

## How Code Is Written Here

All code is Claude-generated. No team member writes code from scratch. The workflow is:
1. Request Claude to generate a Python script or notebook cell
2. Paste into Google Colab and run
3. Paste any error back to Claude for a fix
4. Verify the output (tables, numbers, JSON) — not the source code

When writing code, generate self-contained Colab-compatible Python cells. Prefer output to stdout/CSV so results paste directly into Google Sheets.

## Data Files (Provided by Course)

| File | Contents |
|------|----------|
| `equityBicsV2.csv` | Company identifiers: name, ticker, ISIN, country, BICS sector hierarchy |
| `esgEnvironmentalSocialConsolidatedV4.csv` | Quantitative E & S metrics: GHG emissions, water usage, Scope 1–3 |
| `esgGovernanceConsolidatedV4.csv` | Governance metrics: board diversity, executive compensation |
| `legalEntityEuTaxonomy.csv` | EU Taxonomy eligibility, potential alignment estimates, green revenue proxy, DNSH indicators |

All four files must be loaded and merged on the identifier present in `equityBicsV2.csv`. Always tag data with a vintage (download date) when writing it to the master sheet.

**Important distinction:** `legalEntityEuTaxonomy.csv` contains eligibility and *potential* alignment — reported alignment coverage is sparse. Never conflate taxonomy eligibility with reported alignment.

## Market Data (Student-sourced)

Fetch via `yfinance` using tickers from `equityBicsV2.csv`. Cache all downloads with a date stamp. Calculate: returns, volatility, drawdown, Sharpe ratio, covariance matrix, WACI.

```python
import yfinance as yf
import pandas as pd

tickers = ["ASML.AS", "SAP.DE"]  # from equityBicsV2.csv
data = yf.download(tickers, start="2020-01-01", end="2025-01-01", auto_adjust=True)["Close"]
data.to_csv("price_data_downloaded_YYYY-MM-DD.csv")
```

## Pipeline Architecture

The pipeline must implement **at least 8** of the 13 possible agents. The team's chosen 8:

| Agent | Tool | Owner |
|-------|------|-------|
| 1. Mandate | Google Docs / Claude | Captain |
| 2. Data Ingestion | Colab + yfinance + CSV merge | Data Engineer |
| 3. ESG Scoring | Google Sheets formula + Colab | ESG Specialist |
| 6. Climate | Colab (WACI calculation) | ESG Specialist |
| 4. Document Intelligence | Claude Projects RAG | RAG Operator |
| 9. Greenwashing | Claude Projects + 8-Test prompt | RAG Operator |
| 11. Portfolio Construction | Colab (ranking/optimisation) | Data Engineer + Captain |
| 13. Reporting | Claude + Google Docs/Sheets | All |

Orchestration connects these agents via **n8n.cloud** (drag-and-drop, no code). Pipeline Operator owns the n8n workflow.

## Greenwashing 8-Test Framework

This is the standard evaluation prompt embedded in every Claude Project. Apply to all 50 candidate stocks.

**8 dimensions to assess per company:**
1. Specificity — exact wording; red flag: vague terms
2. Metric — supporting number; red flag: no numeric backing
3. Baseline — comparison reference; red flag: absent or cherry-picked
4. Target — stated endpoint; red flag: non-binding or missing
5. Time horizon — achievement date; red flag: 2050+ and unverifiable
6. Scope — which division/asset; red flag: ambiguous coverage
7. Verification — external assurance; red flag: self-reported only
8. Consistency — capex/lobbying vs. claims; red flag: contradiction

**Standard RAG prompt for Claude Projects:**
> "You are an ESG forensic analyst. For [COMPANY], analyse the most recent sustainability report and assess each of the 8 greenwashing dimensions. For each dimension provide: (a) direct quote with page number, (b) numerical value or factual statement, (c) red-flag rating (LOW / MED / HIGH / MISSING), and (d) one to two sentences of reasoning. If a dimension has no information, mark it as MISSING — never invent. Output as JSON with 8 fields."

Verification: RAG Operator manually verifies 30% of all extractions. Items driving watchlist/exclusion decisions are 100% verified.

## Portfolio Requirements

| Requirement | Minimum |
|-------------|---------|
| Candidate universe | ≥ 50 companies analysed |
| Final holdings | 15–25 companies |
| Weights | Sum to 100%; no single holding > 10% |
| Sector diversification | ≥ 5 sectors |
| Carbon metric | WACI required |
| ESG metric | E, S, G and aggregate score |
| Biodiversity | ≥ 1 nature-risk proxy (ENCORE / WWF Biodiversity Risk Filter / WRI Aqueduct) |
| Benchmark comparison | Required (STOXX Europe 600 or justified alternative) |
| Greenwashing review | Required for all holdings |
| Exclusion / watchlist | Required with rationale |
| Human override examples | ≥ 3 concrete examples for Q&A defence |

## Document Corpus (RAG)

Curate 15–20 PDFs in a local folder. Cover 8–10 material companies including major holdings and exclusions. At minimum 10 primary company documents (annual reports, sustainability reports, TCFD, CSRD/ESRS). Supplement with ENCORE, WWF, WRI Aqueduct, SBTi, TPI, regulatory filings, NGO datasets.

Store in Claude Projects (~12 projects). One project per company corpus or per agent role.

## Key Deliverables Checklist

- [ ] One-page mandate + 3-sentence investment thesis
- [ ] Master data spreadsheet (50 stocks, vintage-tagged)
- [ ] ESG scores per stock (E, S, G, aggregate)
- [ ] WACI calculation
- [ ] Biodiversity proxy scores (50 stocks)
- [ ] Greenwashing 8-Test results per stock (JSON)
- [ ] Verified extraction table (30% sample + 100% watchlist)
- [ ] Final 20-stock portfolio with weights
- [ ] n8n pipeline diagram (required in appendix)
- [ ] Data dictionary (required in appendix)
- [ ] AI Use Statement (required in appendix)
- [ ] One-page portfolio factsheet
- [ ] Written report (5,000–6,500 words, 12 sections)
- [ ] 8–10 slide presentation deck
- [ ] Pre-recorded demo video (Plan B contingency)

## Data Dictionary Format

Every variable must be classified as: **reported / observed / estimated / AI-extracted / judgement-based**

| Variable | Definition | Unit | Source | Extraction method | Data type | Confidence |
|----------|-----------|------|--------|-------------------|-----------|------------|
| Scope 1 emissions | Direct GHG emissions | tCO₂e | Sustainability report | AI extraction + manual check | Reported | High |

## Role Summary

| Role | Owner | Primary tools |
|------|-------|---------------|
| Captain | — | Google Docs, Claude Pro |
| Data Engineer | — | Google Colab, yfinance, Google Sheets |
| ESG Specialist | — | Claude Pro, Google Sheets |
| Pipeline Operator | — | n8n.cloud, Claude Pro, Anthropic API |
| RAG Operator | — | Claude Projects (~12), Google Sheets |

## Hallucination Controls

- Never invent data, sources, or citations
- All Claude Projects outputs marked MISSING if information is absent
- 30% random sample of RAG extractions manually verified against source PDF with page number
- 100% of watchlist/exclusion decisions verified independently
- ESG ratings treated as indicators, not objective truth
- All financial figures cross-checked against yfinance or primary source
