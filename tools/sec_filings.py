import requests

import config
from cache.cache import cached

HEADERS = {"User-Agent": f"investment-research-agent ({config.SEC_EDGAR_CONTACT})"}


@cached("sec_cik_lookup")
def get_cik(ticker: str) -> str | None:
    """Map a ticker to its SEC CIK number."""
    url = "https://www.sec.gov/files/company_tickers.json"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    ticker = ticker.upper()
    for entry in data.values():
        if entry.get("ticker") == ticker:
            return str(entry["cik_str"]).zfill(10)
    return None


@cached("sec_recent_filings")
def get_recent_filings(ticker: str, limit: int = 5) -> list:
    """Return the most recent filings (10-K, 10-Q, 8-K, etc.)"""
    cik = get_cik(ticker)
    if not cik:
        return [{"error": f"No CIK found for ticker {ticker}"}]

    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accession_numbers = recent.get("accessionNumber", [])
    primary_docs = recent.get("primaryDocument", [])

    filings = []
    for i in range(min(limit, len(forms))):
        acc_no_nodash = accession_numbers[i].replace("-", "")
        filings.append({
            "form": forms[i],
            "date": dates[i],
            "url": (
                f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
                f"{acc_no_nodash}/{primary_docs[i]}"
            ),
        })
    return filings