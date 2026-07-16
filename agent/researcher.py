from tools import market_data, sec_filings, web_search

"""
Routes each sub-question to the most relevant free data tool. 
Uses simple keyword heuristics no extra api call cost to decide tool usage.
"""

def research(ticker: str, question: str) -> dict:
    q = question.lower()

    if any(word in q for word in ["financial", "fundamentals", "valuation", "margin", "debt", "cash"]):
        return {
            "source": "yfinance",
            "data": market_data.get_market_snapshot(ticker),
        }

    if any(word in q for word in ["filing", "10-k", "10-q", "8-k", "annual report", "sec"]):
        return {
            "source": "sec_edgar",
            "data": sec_filings.get_recent_filings(ticker),
        }

    if any(word in q for word in ["news", "catalyst", "recent", "event"]):
        return {
            "source": "yfinance_news",
            "data": market_data.get_recent_news(ticker),
        }

    if any(word in q for word in ["price", "performance", "trend", "return"]):
        return {
            "source": "yfinance_price_history",
            "data": market_data.get_price_history(ticker),
        }

    # Default fallback, webb search
    return {
        "source": "web_search",
        "data": web_search.search_web(f"{ticker} {question}"),
    }