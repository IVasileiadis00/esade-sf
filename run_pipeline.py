"""
ESADE Sustainable Finance Pipeline — Master Runner
Executes all 12 agent notebooks in the correct order.
Run this from VS Code (Terminal > Run Task > Run Full Pipeline)
or double-click run_pipeline.bat
"""

import subprocess
import sys
import os
import time
from datetime import datetime

NOTEBOOKS = [
    ("Agent 01 — Mandate",               "notebooks/agent01_mandate.ipynb"),
    ("Agent 02 — Data Ingestion",        "notebooks/agent02_data_ingestion.ipynb"),
    ("Agent 03 — Data Quality",          "notebooks/agent03_data_quality.ipynb"),
    ("Agent 04 — Document Intelligence", "notebooks/agent04_document_intelligence.ipynb"),
    ("Agent 05/06 — ESG & Climate",      "notebooks/agent05_06_esg_climate.ipynb"),
    ("Agent 07 — Biodiversity",          "notebooks/agent07_biodiversity.ipynb"),
    ("Agent 08 — EU Regulation",         "notebooks/agent08_eu_regulation.ipynb"),
    ("Agent 09 — Greenwashing",          "notebooks/agent09_greenwashing.ipynb"),
    ("Agent 10 — Financial Analysis",    "notebooks/agent10_financial_analysis.ipynb"),
    ("Agent 11 — Portfolio Construction","notebooks/agent11_portfolio_construction.ipynb"),
    ("Agent 12 — Human Review",          "notebooks/agent12_human_review.ipynb"),
    ("Agent 13 — Reporting",             "notebooks/agent13_reporting.ipynb"),
]

PYTHON = os.path.join(os.path.dirname(__file__), "venv", "Scripts", "python.exe")
if not os.path.exists(PYTHON):
    PYTHON = sys.executable  # fallback to system python

WIDTH = 65

def banner(text, char="="):
    print(char * WIDTH)
    print(f"  {text}")
    print(char * WIDTH)

def status_line(label, result, elapsed):
    icon = "OK" if result == "OK" else "!!"
    print(f"  [{icon}] {label:<44} {result:<8} {elapsed:.1f}s")

def run_notebook(path):
    cmd = [
        PYTHON, "-m", "jupyter", "nbconvert",
        "--to", "notebook",
        "--execute",
        "--inplace",
        "--ExecutePreprocessor.timeout=300",
        "--ExecutePreprocessor.kernel_name=sustainable-finance",
        path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print()
    banner("ESADE SUSTAINABLE FINANCE PIPELINE")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Agents:  {len(NOTEBOOKS)}")
    print()

    results = []
    total_start = time.time()

    for label, path in NOTEBOOKS:
        print(f"  Running {label}...")
        t0 = time.time()

        if not os.path.exists(path):
            elapsed = time.time() - t0
            status_line(label, "SKIP", elapsed)
            results.append((label, "SKIP", elapsed))
            print(f"         (file not found: {path})")
            continue

        ok, stderr = run_notebook(path)
        elapsed = time.time() - t0

        if ok:
            status_line(label, "OK", elapsed)
            results.append((label, "OK", elapsed))
        else:
            status_line(label, "FAILED", elapsed)
            results.append((label, "FAILED", elapsed))
            # Print last 5 lines of error for diagnosis
            lines = [l for l in stderr.strip().splitlines() if l.strip()]
            for line in lines[-5:]:
                print(f"         {line}")

        print()

    # Summary
    total = time.time() - total_start
    ok_count   = sum(1 for _, r, _ in results if r == "OK")
    fail_count = sum(1 for _, r, _ in results if r == "FAILED")
    skip_count = sum(1 for _, r, _ in results if r == "SKIP")

    banner("PIPELINE COMPLETE", "-")
    print(f"  Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Total time: {total:.1f}s")
    print()
    print(f"  Passed:  {ok_count} agents")
    print(f"  Failed:  {fail_count} agents")
    print(f"  Skipped: {skip_count} agents")
    print()

    if fail_count == 0 and skip_count == 0:
        print("  All agents ran successfully.")
        print("  Check outputs/ folder for results.")
    elif fail_count > 0:
        print("  Some agents failed. Review errors above.")
        print("  Fix the issue and re-run — completed agents are saved.")
    else:
        print("  Pipeline ran with skips. Check missing notebook paths.")

    print("=" * WIDTH)
    print()

    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
