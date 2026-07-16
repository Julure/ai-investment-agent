import yfinance as yf

from cache.cache import cached


def _fmt_billions(value):
    if value is None:
        return None
    if value >= 1e12:
        return f"${value / 1e12:.2f}T"
    return f"${value / 1e9:.2f}B"


def _fmt_pct(value):
    if value is None:
        return None
    return f"{value * 100:.1f}%"


@cached("market_snapshot")
def get_market_snapshot(ticker: str) -> dict:
    """Return a compact, CLEARLY LABELED snapshot: price, valuation ratios"""
    t = yf.Ticker(ticker)
    info = t.info or {}

    return {
        "company_name": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "current_price": info.get("currentPrice"),
        "market_cap": _fmt_billions(info.get("marketCap")),
        "trailing_pe_ratio": info.get("trailingPE"),
        "forward_pe_ratio": info.get("forwardPE"),
        "price_to_book_ratio": info.get("priceToBook"),
        "dividend_yield": _fmt_pct(info.get("dividendYield")),
        "gross_margin": _fmt_pct(info.get("grossMargins")),
        "net_profit_margin": _fmt_pct(info.get("profitMargins")),
        "operating_margin": _fmt_pct(info.get("operatingMargins")),
        "revenue_growth_yoy": _fmt_pct(info.get("revenueGrowth")),
        "earnings_growth_yoy": _fmt_pct(info.get("earningsGrowth")),
        "total_revenue": _fmt_billions(info.get("totalRevenue")),
        "total_debt": _fmt_billions(info.get("totalDebt")),
        "total_cash": _fmt_billions(info.get("totalCash")),
        "free_cash_flow": _fmt_billions(info.get("freeCashflow")),
        "return_on_equity": _fmt_pct(info.get("returnOnEquity")),
        "analyst_recommendation": info.get("recommendationKey"),
        "analyst_target_price": info.get("targetMeanPrice"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
    }


@cached("price_history")
def get_price_history(ticker: str, period: str = "1y") -> dict:
    """Return summary stats over a period rather than the full raw series,
    to keep the payload small for the LLM."""
    t = yf.Ticker(ticker)
    hist = t.history(period=period)
    if hist.empty:
        return {"error": f"No price history found for {ticker}"}

    close = hist["Close"]
    return {
        "period": period,
        "start_price": round(float(close.iloc[0]), 2),
        "end_price": round(float(close.iloc[-1]), 2),
        "pct_change": round(float((close.iloc[-1] / close.iloc[0] - 1) * 100), 2),
        "high": round(float(close.max()), 2),
        "low": round(float(close.min()), 2),
        "avg_volume": int(hist["Volume"].mean()),
    }


@cached("recent_news")
def get_recent_news(ticker: str, limit: int = 5) -> list:
    t = yf.Ticker(ticker)
    news = t.news or []
    company_name = (t.info or {}).get("longName", "")
    name_hint = company_name.split(",")[0].split(" Inc")[0].strip().lower()

    out = []
    for item in news:
        content = item.get("content", item)  # yfinance news schema varies by version
        title = content.get("title") or ""

        is_relevant = ticker.lower() in title.lower() or (
            name_hint and name_hint in title.lower()
        )
        if not is_relevant:
            continue

        out.append({
            "title": title,
            "publisher": content.get("provider", {}).get("displayName")
                if isinstance(content.get("provider"), dict) else content.get("publisher"),
            "link": content.get("canonicalUrl", {}).get("url")
                if isinstance(content.get("canonicalUrl"), dict) else content.get("link"),
        })
        if len(out) >= limit:
            break

    if not out:
        return [{"note": f"No {ticker}-specific headlines found in the current feed."}]
    return out