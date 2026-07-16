import yfinance as yf
from cache.cache import cached


@cached("market_snapshot")
def get_market_snapshot(ticker: str) -> dict:
    """Compat snapshot of price, valuation ratios, and key fundamentals."""
    t = yf.Ticker(ticker)
    info = t.info or {}

    keys = [
        "longName", "sector", "industry", "currentPrice", "marketCap",
        "trailingPE", "forwardPE", "priceToBook", "dividendYield",
        "profitMargins", "revenueGrowth", "earningsGrowth", "totalRevenue",
        "totalDebt", "totalCash", "freeCashflow", "returnOnEquity",
        "recommendationKey", "targetMeanPrice", "fiftyTwoWeekHigh",
        "fiftyTwoWeekLow",
    ]
    return {k: info.get(k) for k in keys}


@cached("price_history")
def get_price_history(ticker: str, period: str = "1y") -> dict:
    """Return summary of stats over a period of time instead of raw data for llm token optimization"""
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
    out = []
    for item in news[:limit]:
        content = item.get("content", item)  #! yfinance news schema can vary by content double check if this works
        out.append({
            "title": content.get("title"),
            "publisher": content.get("provider", {}).get("displayName")
                if isinstance(content.get("provider"), dict) else content.get("publisher"),
            "link": content.get("canonicalUrl", {}).get("url")
                if isinstance(content.get("canonicalUrl"), dict) else content.get("link"),
        })
    return out