import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_connection import get_properties, get_financials
from sec_edgar import get_sec_financials

def query_financials(metric: str = "all") -> dict:
    """
    Retrieve financial data from the real estate portfolio database.
    Use this when the user asks about revenue, net income, expenses,
    or any financial performance metrics.

    Args:
        metric: One of "revenue", "net_income", "expenses", or "all".

    Returns:
        A dictionary with the requested financial figures.
    """
    df = get_financials()

    if metric == "revenue":
        return {"total_revenue": float(df["revenue"].sum())}
    elif metric == "net_income":
        return {"total_net_income": float(df["net_income"].sum())}
    elif metric == "expenses":
        return {"total_expenses": float(df["expenses"].sum())}
    else:
        return {
            "total_revenue": float(df["revenue"].sum()),
            "total_net_income": float(df["net_income"].sum()),
            "total_expenses": float(df["expenses"].sum()),
            "property_count": len(df)
        }


def query_properties(metro_area: str = None, property_type: str = None) -> dict:
    """
    Retrieve property records from the database, optionally filtered
    by metro area or property type.
    Use this when the user asks about properties, locations, square footage,
    or portfolio composition.

    Args:
        metro_area: Optional metro area name to filter by (e.g. "Chicago", "Miami").
        property_type: Optional type to filter by (e.g. "industrial", "office", "retail").

    Returns:
        A dictionary with a list of matching properties and a count.
    """
    df = get_properties()

    if metro_area:
        df = df[df["metro_area"].str.lower().str.contains(metro_area.lower(), na=False)]
    if property_type:
        df = df[df["property_type"].str.lower().str.contains(property_type.lower(), na=False)]

    records = df.to_dict(orient="records")
    return {
        "count": len(records),
        "properties": records
    }


def query_press_releases(topic: str = None) -> dict:
    """
    Search recent company press releases for news about acquisitions,
    expansions, earnings, or other corporate updates.
    Use this when the user asks about announcements, news, or recent events.

    Args:
        topic: Optional keyword to filter press releases (e.g. "acquisition", "earnings").

    Returns:
        A dictionary with matching press release titles, dates, and summaries.
    """
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'press_releases.json')
    with open(path, "r") as f:
        releases = json.load(f)

    if topic:
        keyword = topic.lower()
        releases = [
            r for r in releases
            if keyword in r["title"].lower() or keyword in r["summary"].lower()
        ]

    return {
        "count": len(releases),
        "press_releases": releases
    }

def query_sec_filings(filing_type: str = "10-K") -> dict:
    """
    Fetch real financial data for Prologis, Inc. directly from SEC EDGAR.
    Use this when the user asks about SEC filings, reported financials,
    annual or quarterly earnings, revenue from official reports,
    or anything referencing 10-K or 10-Q documents.

    Args:
        filing_type: "10-K" for annual filings, "10-Q" for quarterly filings.

    Returns:
        A dictionary with revenue, net income, and operating expenses
        from the most recent SEC filings.
    """
    return get_sec_financials(form=filing_type)