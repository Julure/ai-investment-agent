import time

from langchain_groq import ChatGroq

import config

_last_call_time = 0.0

_fast_llm = ChatGroq(model=config.MODEL_FAST, api_key=config.GROQ_API_KEY, temperature=0.2)
_smart_llm = ChatGroq(model=config.MODEL_SMART, api_key=config.GROQ_API_KEY, temperature=0.3)


def _pace():
    """Sleep to stay under free-tier requests-per-minute limits."""
    global _last_call_time
    elapsed = time.monotonic() - _last_call_time
    wait = config.MIN_SECONDS_BETWEEN_CALLS - elapsed
    if wait > 0:
        time.sleep(wait)
    _last_call_time = time.monotonic()


def invoke(prompt: str, smart: bool = False) -> str:
    """Call Groq with pacing + retry/backoff on rate-limit errors."""
    llm = _smart_llm if smart else _fast_llm

    for attempt in range(config.MAX_RETRIES):
        _pace()
        try:
            return llm.invoke(prompt).content
        except Exception as e:
            is_rate_limit = "429" in str(e) or "rate" in str(e).lower()
            if is_rate_limit and attempt < config.MAX_RETRIES - 1:
                time.sleep(config.RETRY_BACKOFF_SECONDS * (attempt + 1))
                continue
            raise