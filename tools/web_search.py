from ddgs import DDGS

from cache.cache import cached


@cached("web_search")
def search_web(query: str, max_results: int = 5) -> list:
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
    return [
        {"title": r.get("title"), "snippet": r.get("body"), "url": r.get("href")}
        for r in results
    ]