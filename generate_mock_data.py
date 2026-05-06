"""
Generates mock versions of the four course CSV files.
Uses ~55 real European companies from the STOXX Europe 600 universe.
Replace with the real professor-provided files on Friday.
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)
OUT = "data/provided"
os.makedirs(OUT, exist_ok=True)

# ── 55 companies ────────────────────────────────────────────────────────────
companies = [
    # name, ticker, isin, country, bics_l1, bics_l2, bics_l3, bics_l4
    ("ASML Holding",        "ASML.AS",   "NL0010273215", "Netherlands", "Technology",          "Semiconductors",              "Semiconductor Equipment",       "Lithography Equipment"),
    ("SAP SE",              "SAP.DE",    "DE0007164600", "Germany",     "Technology",          "Software",                    "Enterprise Software",           "ERP Systems"),
    ("Capgemini",           "CAP.PA",    "FR0000125338", "France",      "Technology",          "IT Services",                 "Consulting",                    "Digital Transformation"),
    ("Amadeus IT Group",    "AMS.MC",    "ES0109067019", "Spain",       "Technology",          "Software",                    "Travel Technology",             "GDS Platforms"),
    ("Hexagon AB",          "HEXA-B.ST", "SE0015961909", "Sweden",      "Technology",          "Industrial Software",         "Measurement Technology",        "Geospatial Solutions"),
    ("Siemens AG",          "SIE.DE",    "DE0007236101", "Germany",     "Industrials",         "Electrical Equipment",        "Automation",                    "Industrial Automation"),
    ("ABB Ltd",             "ABBN.SW",   "CH0012221716", "Switzerland", "Industrials",         "Electrical Equipment",        "Power & Automation",            "Robotics"),
    ("Schneider Electric",  "SU.PA",     "FR0000121972", "France",      "Industrials",         "Electrical Equipment",        "Energy Management",             "Smart Buildings"),
    ("Airbus SE",           "AIR.PA",    "NL0000235190", "Netherlands", "Industrials",         "Aerospace & Defense",         "Commercial Aircraft",           "Commercial Aviation"),
    ("Rolls-Royce Holdings","RR.L",      "GB00B63H8491", "UK",          "Industrials",         "Aerospace & Defense",         "Engines",                       "Aerospace Engines"),
    ("Vestas Wind Systems", "VWS.CO",    "DK0061539921", "Denmark",     "Industrials",         "Industrial Equipment",        "Renewable Energy Equipment",    "Wind Turbines"),
    ("Legrand SA",          "LR.PA",     "FR0010307819", "France",      "Industrials",         "Electrical Equipment",        "Wiring Devices",                "Building Infrastructure"),
    ("Novartis AG",         "NOVN.SW",   "CH0012005267", "Switzerland", "Healthcare",          "Pharmaceuticals",             "Innovative Medicines",          "Oncology"),
    ("Roche Holding",       "ROG.SW",    "CH0012032048", "Switzerland", "Healthcare",          "Pharmaceuticals",             "Diagnostics & Pharma",          "Personalised Medicine"),
    ("AstraZeneca",         "AZN.L",     "GB0009895292", "UK",          "Healthcare",          "Pharmaceuticals",             "Biopharmaceuticals",            "Oncology & Cardiovascular"),
    ("Novo Nordisk",        "NOVO-B.CO", "DK0060534915", "Denmark",     "Healthcare",          "Pharmaceuticals",             "Diabetes Care",                 "GLP-1 Therapies"),
    ("Sanofi",              "SAN.PA",    "FR0000120578", "France",      "Healthcare",          "Pharmaceuticals",             "Specialty Care",                "Vaccines & Immunology"),
    ("Lonza Group",         "LONN.SW",   "CH0013841017", "Switzerland", "Healthcare",          "Life Sciences",               "CDMO",                          "Biologics Manufacturing"),
    ("TotalEnergies SE",    "TTE.PA",    "FR0014000MR3", "France",      "Energy",              "Integrated Oil & Gas",        "Upstream & Downstream",         "LNG & Renewables"),
    ("Shell plc",           "SHEL.L",    "GB00BP6MXD84", "UK",          "Energy",              "Integrated Oil & Gas",        "Global Energy",                 "Transition Energy"),
    ("Equinor ASA",         "EQNR.OL",   "NO0010096985", "Norway",      "Energy",              "Integrated Oil & Gas",        "Offshore Operator",             "Norwegian Continental Shelf"),
    ("Orsted AS",           "ORSTED.CO", "DK0060094928", "Denmark",     "Utilities",           "Renewable Energy",            "Offshore Wind",                 "Offshore Wind Development"),
    ("Iberdrola SA",        "IBE.MC",    "ES0144580Y14", "Spain",       "Utilities",           "Electric Utilities",          "Regulated Networks",            "Renewables & Networks"),
    ("RWE AG",              "RWE.DE",    "DE0007037129", "Germany",     "Utilities",           "Electric Utilities",          "Conventional & Renewables",     "Offshore Wind & Gas"),
    ("Enel SpA",            "ENEL.MI",   "IT0003128367", "Italy",       "Utilities",           "Electric Utilities",          "Integrated Utility",            "Renewable Generation"),
    ("BNP Paribas",         "BNP.PA",    "FR0000131104", "France",      "Financial Services",  "Banks",                       "Diversified Banking",           "Corporate & Investment Bank"),
    ("HSBC Holdings",       "HSBA.L",    "GB0005405286", "UK",          "Financial Services",  "Banks",                       "Global Banking",                "Retail & Commercial"),
    ("ING Groep",           "INGA.AS",   "NL0011821202", "Netherlands", "Financial Services",  "Banks",                       "Retail Banking",                "Digital Banking"),
    ("UniCredit SpA",       "UCG.MI",    "IT0005239360", "Italy",       "Financial Services",  "Banks",                       "Pan-European Banking",          "Corporate Banking"),
    ("AXA SA",              "CS.PA",     "FR0000120628", "France",      "Financial Services",  "Insurance",                   "Multi-line Insurance",          "Life & P&C"),
    ("Allianz SE",          "ALV.DE",    "DE0008404005", "Germany",     "Financial Services",  "Insurance",                   "Multi-line Insurance",          "Asset Management"),
    ("Zurich Insurance",    "ZURN.SW",   "CH0011075394", "Switzerland", "Financial Services",  "Insurance",                   "General Insurance",             "Commercial Lines"),
    ("Unilever plc",        "ULVR.L",    "GB00B10RZP78", "UK",          "Consumer Staples",    "Food & Beverage",             "Personal Care & Foods",         "FMCG"),
    ("Nestle SA",           "NESN.SW",   "CH0012221716", "Switzerland", "Consumer Staples",    "Food & Beverage",             "Packaged Foods",                "Nutrition & Wellness"),
    ("Danone SA",           "BN.PA",     "FR0000120644", "France",      "Consumer Staples",    "Food & Beverage",             "Dairy & Plant-Based",           "Specialised Nutrition"),
    ("Heineken NV",         "HEIA.AS",   "NL0000009165", "Netherlands", "Consumer Staples",    "Food & Beverage",             "Beverages",                     "Beer"),
    ("Carlsberg AS",        "CARL-B.CO", "DK0010181759", "Denmark",     "Consumer Staples",    "Food & Beverage",             "Beverages",                     "Beer"),
    ("L'Oreal SA",          "OR.PA",     "FR0000120321", "France",      "Consumer Discretionary","Personal Products",         "Beauty",                        "Skincare & Cosmetics"),
    ("LVMH",                "MC.PA",     "FR0000121014", "France",      "Consumer Discretionary","Luxury Goods",              "Fashion & Leather",             "Wines & Spirits"),
    ("Inditex",             "ITX.MC",    "ES0148396007", "Spain",       "Consumer Discretionary","Retail",                   "Apparel Retail",                "Fast Fashion"),
    ("Adidas AG",           "ADS.DE",    "DE000A1EWWW0", "Germany",     "Consumer Discretionary","Apparel & Footwear",        "Sportswear",                    "Performance & Lifestyle"),
    ("Pernod Ricard",       "RI.PA",     "FR0000120693", "France",      "Consumer Staples",    "Food & Beverage",             "Spirits",                       "Premium Spirits"),
    ("BASF SE",             "BAS.DE",    "DE000BASF111", "Germany",     "Materials",           "Chemicals",                   "Diversified Chemicals",         "Performance Products"),
    ("Air Liquide",         "AI.PA",     "FR0000120073", "France",      "Materials",           "Chemicals",                   "Industrial Gases",              "Healthcare Gases"),
    ("ArcelorMittal",       "MT.AS",     "LU1598757687", "Luxembourg",  "Materials",           "Metals & Mining",             "Steel",                         "Flat & Long Steel"),
    ("Holcim AG",           "HOLN.SW",   "CH0012214059", "Switzerland", "Materials",           "Construction Materials",      "Cement & Aggregates",           "Low-Carbon Building"),
    ("Volkswagen AG",       "VOW3.DE",   "DE0007664039", "Germany",     "Consumer Discretionary","Automotive",               "Passenger Vehicles",            "EV Transition"),
    ("BMW AG",              "BMW.DE",    "DE0005190003", "Germany",     "Consumer Discretionary","Automotive",               "Luxury Vehicles",               "Electric Mobility"),
    ("Stellantis NV",       "STLAM.MI",  "NL00150001Q9", "Netherlands", "Consumer Discretionary","Automotive",               "Multi-Brand Vehicles",          "EV & Combustion"),
    ("Volvo AB",            "VOLV-B.ST", "SE0000115446", "Sweden",      "Industrials",         "Commercial Vehicles",         "Trucks & Buses",                "Electrified Transport"),
    ("Renault SA",          "RNO.PA",    "FR0000131906", "France",      "Consumer Discretionary","Automotive",               "Passenger Vehicles",            "EV Transition"),
    ("Deutsche Telekom",    "DTE.DE",    "DE0005557508", "Germany",     "Telecommunications",  "Telecom Services",            "Integrated Telco",              "Fixed & Mobile"),
    ("Orange SA",           "ORA.PA",    "FR0000133308", "France",      "Telecommunications",  "Telecom Services",            "Integrated Telco",              "B2B Services"),
    ("Vodafone Group",      "VOD.L",     "GB00BH4HKS39", "UK",          "Telecommunications",  "Telecom Services",            "Mobile Networks",               "European Mobile"),
    ("Vonovia SE",          "VNA.DE",    "DE000A1ML7J1", "Germany",     "Real Estate",         "Residential REITs",           "Residential Property",          "German Residential"),
    ("Gecina SA",           "GFC.PA",    "FR0010040865", "France",      "Real Estate",         "Commercial REITs",            "Office & Residential",          "Paris Office Market"),
]

isins      = [c[2] for c in companies]
tickers    = [c[1] for c in companies]
n = len(companies)

# ── FILE 1: equityBicsV2.csv ─────────────────────────────────────────────────
df1 = pd.DataFrame({
    "companyName":  [c[0] for c in companies],
    "ticker":       tickers,
    "isin":         isins,
    "country":      [c[3] for c in companies],
    "bics_sector":  [c[4] for c in companies],
    "bics_industry":[c[5] for c in companies],
    "bics_sub_industry": [c[6] for c in companies],
    "bics_activity":[c[7] for c in companies],
    "market_cap_eur_bn": np.round(np.random.uniform(5, 350, n), 1),
    "index_weight_pct":  np.round(np.random.uniform(0.1, 3.5, n), 3),
})
df1.to_csv(f"{OUT}/equityBicsV2.csv", index=False)
print(f"Saved equityBicsV2.csv  — {len(df1)} companies")

# ── FILE 2: esgEnvironmentalSocialConsolidatedV4.csv ────────────────────────
# Scale emissions roughly by sector realism
sector_emission_multiplier = {
    "Energy": 8.0, "Utilities": 6.0, "Materials": 5.0,
    "Industrials": 2.0, "Consumer Staples": 1.5,
    "Consumer Discretionary": 1.2, "Healthcare": 0.8,
    "Telecommunications": 0.7, "Financial Services": 0.4,
    "Technology": 0.5, "Real Estate": 1.0,
}

scope1, scope2, scope3, energy, water, waste = [], [], [], [], [], []
for c in companies:
    mult = sector_emission_multiplier.get(c[4], 1.5)
    s1 = round(np.random.uniform(50_000, 8_000_000) * mult)
    s2 = round(np.random.uniform(20_000, 2_000_000) * mult * 0.4)
    s3 = round(s1 * np.random.uniform(3, 15))  # scope 3 always bigger
    e  = round(np.random.uniform(500, 80_000) * mult, 1)
    w  = round(np.random.uniform(100_000, 50_000_000) * (mult / 2))
    wst= round(np.random.uniform(5_000, 500_000) * mult)
    scope1.append(s1); scope2.append(s2); scope3.append(s3)
    energy.append(e);  water.append(w);   waste.append(wst)

df2 = pd.DataFrame({
    "isin":                          isins,
    "reporting_year":                [2023] * n,
    "scope1_emissions_tco2e":        scope1,
    "scope2_emissions_market_tco2e": scope2,
    "scope2_emissions_location_tco2e": [round(s * np.random.uniform(0.9, 1.3)) for s in scope2],
    "scope3_emissions_tco2e":        scope3,
    "scope3_categories_reported":    np.random.randint(3, 15, n),
    "total_energy_consumption_gwh":  energy,
    "renewable_energy_pct":          np.round(np.random.uniform(5, 85, n), 1),
    "energy_intensity_mwh_per_eur_m_revenue": np.round(np.random.uniform(10, 800, n), 1),
    "water_withdrawal_m3":           water,
    "water_consumption_m3":          [round(w * np.random.uniform(0.4, 0.8)) for w in water],
    "water_stress_area_pct":         np.round(np.random.uniform(5, 65, n), 1),
    "waste_generated_tonnes":        waste,
    "waste_recycled_pct":            np.round(np.random.uniform(20, 85, n), 1),
    "hazardous_waste_tonnes":        [round(w * np.random.uniform(0.01, 0.10)) for w in waste],
    "employees_total":               np.random.randint(3_000, 350_000, n),
    "women_in_workforce_pct":        np.round(np.random.uniform(25, 65, n), 1),
    "gender_pay_gap_pct":            np.round(np.random.uniform(-5, 25, n), 1),
    "employee_turnover_pct":         np.round(np.random.uniform(3, 18, n), 1),
    "training_hours_per_employee":   np.round(np.random.uniform(10, 60, n), 1),
    "work_related_injury_rate":      np.round(np.random.uniform(0.1, 4.5, n), 2),
    "fatalities":                    np.random.choice([0, 0, 0, 1, 2], n),
    "supplier_esg_audits_pct":       np.round(np.random.uniform(10, 90, n), 1),
    "community_investment_eur_m":    np.round(np.random.uniform(1, 250, n), 1),
    "carbon_intensity_tco2e_per_eur_m_revenue": np.round(np.array(scope1) / np.random.uniform(500, 5000, n), 1),
    "sbti_status":                   np.random.choice(["Committed", "Targets Set", "Not Committed", "Approved"], n, p=[0.25, 0.35, 0.25, 0.15]),
    "net_zero_target_year":          np.random.choice([2040, 2045, 2050, None, None], n),
})

# Introduce some realistic missing values (Scope 3 and water often missing)
missing_mask_s3  = np.random.random(n) < 0.20
missing_mask_wat = np.random.random(n) < 0.15
df2.loc[missing_mask_s3,  "scope3_emissions_tco2e"] = None
df2.loc[missing_mask_wat, "water_withdrawal_m3"]    = None
df2.loc[missing_mask_wat, "water_consumption_m3"]   = None

df2.to_csv(f"{OUT}/esgEnvironmentalSocialConsolidatedV4.csv", index=False)
print(f"Saved esgEnvironmentalSocialConsolidatedV4.csv  — {len(df2)} rows")

# ── FILE 3: esgGovernanceConsolidatedV4.csv ──────────────────────────────────
df3 = pd.DataFrame({
    "isin":                              isins,
    "reporting_year":                    [2023] * n,
    "board_size":                        np.random.randint(8, 20, n),
    "board_independence_pct":            np.round(np.random.uniform(45, 90, n), 1),
    "women_on_board_pct":                np.round(np.random.uniform(25, 55, n), 1),
    "ceo_chair_separation":              np.random.choice([1, 0], n, p=[0.75, 0.25]),
    "ceo_tenure_years":                  np.random.randint(1, 15, n),
    "audit_committee_independence_pct":  np.round(np.random.uniform(75, 100, n), 1),
    "remuneration_committee_independence_pct": np.round(np.random.uniform(70, 100, n), 1),
    "ceo_pay_ratio":                     np.random.randint(20, 280, n),
    "executive_pay_esg_linked_pct":      np.round(np.random.uniform(0, 40, n), 1),
    "say_on_pay_approval_pct":           np.round(np.random.uniform(65, 99, n), 1),
    "shareholder_rights_score_0_100":    np.random.randint(45, 95, n),
    "anti_corruption_policy":            np.random.choice([1, 0], n, p=[0.92, 0.08]),
    "whistleblower_policy":              np.random.choice([1, 0], n, p=[0.88, 0.12]),
    "data_privacy_policy":               np.random.choice([1, 0], n, p=[0.95, 0.05]),
    "lobbying_disclosure":               np.random.choice([1, 0], n, p=[0.60, 0.40]),
    "political_donations_eur_k":         np.random.choice([0, 0, 0, 50, 100, 250], n),
    "tax_transparency_report":           np.random.choice([1, 0], n, p=[0.70, 0.30]),
    "esg_committee_at_board_level":      np.random.choice([1, 0], n, p=[0.65, 0.35]),
    "external_esg_assurance":            np.random.choice(["Limited", "Reasonable", "None", "Limited"], n, p=[0.50, 0.15, 0.20, 0.15]),
    "assurance_provider":                np.random.choice(["Deloitte", "PwC", "KPMG", "EY", "Bureau Veritas", "None"], n),
    "ungc_signatory":                    np.random.choice([1, 0], n, p=[0.72, 0.28]),
    "controversies_score_0_10":          np.round(np.random.uniform(0, 7, n), 1),
})

# Some realistic missing values
for col in ["ceo_pay_ratio", "executive_pay_esg_linked_pct", "lobbying_disclosure"]:
    mask = np.random.random(n) < 0.12
    df3.loc[mask, col] = None

df3.to_csv(f"{OUT}/esgGovernanceConsolidatedV4.csv", index=False)
print(f"Saved esgGovernanceConsolidatedV4.csv  — {len(df3)} rows")

# ── FILE 4: legalEntityEuTaxonomy.csv ────────────────────────────────────────
# Eligibility varies by sector; alignment is sparse
sector_eligibility = {
    "Utilities": (55, 75), "Energy": (20, 40), "Industrials": (25, 50),
    "Materials": (15, 35), "Technology": (10, 25), "Healthcare": (5, 20),
    "Consumer Discretionary": (10, 30), "Consumer Staples": (5, 20),
    "Financial Services": (15, 40), "Telecommunications": (5, 15),
    "Real Estate": (35, 65),
}

elig_turn, align_turn, elig_capex, align_capex = [], [], [], []
for c in companies:
    lo, hi = sector_eligibility.get(c[4], (10, 30))
    et = round(np.random.uniform(lo, hi), 1)
    # Alignment is 0–30% of eligibility, frequently missing
    at = round(et * np.random.uniform(0, 0.35), 1) if np.random.random() > 0.45 else None
    ec = round(np.random.uniform(lo * 1.1, hi * 1.3), 1)  # capex elig typically higher
    ac = round(ec * np.random.uniform(0, 0.30), 1) if np.random.random() > 0.50 else None
    elig_turn.append(et); align_turn.append(at)
    elig_capex.append(ec); align_capex.append(ac)

df4 = pd.DataFrame({
    "isin":                                       isins,
    "reporting_year":                             [2023] * n,
    "taxonomy_eligible_turnover_pct":             elig_turn,
    "taxonomy_aligned_turnover_pct":              align_turn,
    "taxonomy_eligible_capex_pct":                elig_capex,
    "taxonomy_aligned_capex_pct":                 align_capex,
    "taxonomy_eligible_opex_pct":                 [round(et * np.random.uniform(0.8, 1.1), 1) for et in elig_turn],
    "taxonomy_aligned_opex_pct":                  [round(at * np.random.uniform(0.7, 1.0), 1) if at else None for at in align_turn],
    "climate_mitigation_eligible":                np.random.choice([1, 0], n, p=[0.70, 0.30]),
    "climate_adaptation_eligible":                np.random.choice([1, 0], n, p=[0.40, 0.60]),
    "water_protection_eligible":                  np.random.choice([1, 0], n, p=[0.25, 0.75]),
    "circular_economy_eligible":                  np.random.choice([1, 0], n, p=[0.35, 0.65]),
    "pollution_prevention_eligible":              np.random.choice([1, 0], n, p=[0.30, 0.70]),
    "biodiversity_eligible":                      np.random.choice([1, 0], n, p=[0.20, 0.80]),
    "dnsh_climate_mitigation":                    np.random.choice(["Met", "Not Met", "N/A", None], n, p=[0.45, 0.10, 0.30, 0.15]),
    "dnsh_climate_adaptation":                    np.random.choice(["Met", "Not Met", "N/A", None], n, p=[0.40, 0.10, 0.35, 0.15]),
    "dnsh_water":                                 np.random.choice(["Met", "Not Met", "N/A", None], n, p=[0.35, 0.10, 0.40, 0.15]),
    "dnsh_circular_economy":                      np.random.choice(["Met", "Not Met", "N/A", None], n, p=[0.38, 0.08, 0.39, 0.15]),
    "dnsh_pollution":                             np.random.choice(["Met", "Not Met", "N/A", None], n, p=[0.40, 0.12, 0.33, 0.15]),
    "dnsh_biodiversity":                          np.random.choice(["Met", "Not Met", "N/A", None], n, p=[0.30, 0.12, 0.43, 0.15]),
    "minimum_social_safeguards":                  np.random.choice(["Met", "Not Met", None], n, p=[0.65, 0.10, 0.25]),
    "green_revenue_proxy_pct":                    [round(et * np.random.uniform(0.8, 1.3), 1) for et in elig_turn],
    "fossil_fuel_revenue_pct":                    [round(np.random.uniform(0, 8), 1) if c[4] in ["Energy"] else round(np.random.uniform(0, 2), 1) for c in companies],
    "taxonomy_disclosure_quality":                np.random.choice(["Full", "Partial", "Minimal"], n, p=[0.30, 0.45, 0.25]),
})

df4.to_csv(f"{OUT}/legalEntityEuTaxonomy.csv", index=False)
print(f"Saved legalEntityEuTaxonomy.csv  — {len(df4)} rows")

print("\nAll 4 mock CSV files saved to data/provided/")
print("Open them in Excel to inspect. Replace with real files on Friday.")
print(f"\nCompanies covered: {n}")
print(f"Sectors: {df1['bics_sector'].nunique()}")
print(df1['bics_sector'].value_counts().to_string())
