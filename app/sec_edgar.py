import requests
import pandas as pd

# Prologis CIK on SEC EDGAR
PROLOGIS_CIK  = "0001045609"
COMPANY_NAME  = "Prologis, Inc."

# SEC requires a User-Agent header identifying your app
HEADERS = {"User-Agent": "financial-assistant hatahet.ah@gmail.com"}


def _fetch_company_facts() -> dict:
    """Download all XBRL facts for Prologis from SEC EDGAR."""
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{PROLOGIS_CIK}.json"
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return response.json()


def _extract_metric(facts: dict, concept: str, form: str = "10-K") -> list:
    """
    Pull a specific US-GAAP concept from the facts blob,
    filtered by filing form type, sorted newest first.
    """
    try:
        records = facts["facts"]["us-gaap"][concept]["units"]["USD"]
        df = pd.DataFrame(records)
        df = df[df["form"] == form].sort_values("end", ascending=False)
        # Drop duplicate periods (keep latest filing for each period)
        df = df.drop_duplicates(subset="end")
        return df[["end", "val", "accn", "form"]].head(5).to_dict(orient="records")
    except KeyError:
        return []


def get_sec_financials(form: str = "10-K") -> dict:
    """
    Fetch recent Prologis financials from SEC EDGAR XBRL API.

    Args:
        form: Filing type — "10-K" for annual, "10-Q" for quarterly.

    Returns:
        Dictionary with revenue, net_income, and operating_expenses records.
    """
    facts = _fetch_company_facts()

    # Revenue — try multiple possible concept names
    revenue = []
    for concept in ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"]:
        revenue = _extract_metric(facts, concept, form)
        if revenue:
            break

    # Net Income
    net_income = _extract_metric(facts, "NetIncomeLoss", form)

    # Operating Expenses
    op_expenses = []
    for concept in ["OperatingExpenses", "CostsAndExpenses"]:
        op_expenses = _extract_metric(facts, concept, form)
        if op_expenses:
            break

    return {
        "company":            COMPANY_NAME,
        "filing_type":        form,
        "revenue":            revenue,
        "net_income":         net_income,
        "operating_expenses": op_expenses,
    }