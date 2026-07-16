# Investment Research Agent

A free, self-hosted deep-research agent that produces structured investment
briefs from public financial data. Built on Groq + LangChain to run at zero
cost no paid APIs, no token billing.

**IMPORTANT! this is not a financial advice tool, this is a research summarization tool.**

## What it does

Given a company or ticker, the agent:

1. Plans a set of research sub-questions (financial health, valuation,
   growth/competitive position, recent news, risks)
2. Routes each sub-question to the right free data source and retrieves it
3. Condenses raw data into analyst-style notes
4. Reviews its own notes for gaps or thin sections, and runs a targeted
   follow-up research round if needed
5. Synthesizes everything into one structured Markdown report

The result is a repeatable, source-grounded research brief, not a single
LLM prompt guessing about a company from memory.

## Stack

- **LLM**: [Groq](https://groq.com) (free tier) `llama-3.1-8b-instant` for
  planning/summarization/critique, `llama-3.3-70b-versatile` for final
  synthesis
- **Orchestration**: LangChain (`langchain-groq`) via LCEL-style chains
- **Data sources**: `yfinance` (price/fundamentals), SEC EDGAR (filings),
  DuckDuckGo Search (news/web context) all free, no API keys required
- **Storage**: SQLite-backed local cache, keyed by input hash, so repeat
  research on the same ticker costs zero additional API calls
- **Environment**: managed with `uv`
- **CLI**: `rich` for progress output

## Project scope

**scope:**

- Multi-source research aggregation for a single company/ticker at a time
- A self-critique loop that can trigger up to N rounds of follow-up research
  when initial findings are incomplete
- Deterministic, keyword-based tool routing (no LLM calls spent deciding
  which tool to use)
- Defensive prompting and data formatting to reduce hallucinated or
  mislabeled financial figures structured numeric data is formatted in
  code rather than paraphrased by the LLM

**Out of scope (for now) / Could be implemented in the future:**

- Investment recommendations, price targets, or buy/sell signals
- Portfolio-level or multi-company comparative analysis
- Real-time/streaming data this is a point-in-time research snapshot
- Authenticated/paid data sources
- A UI this is currently CLI-only

## File structure

investment-agent/
├── main.py # CLI entry point, orchestrates the pipeline
├── config.py # models, rate limits, paths
├── agent/ # planner, researcher, summarizer, critic, synthesizer
├── tools/ # yfinance, SEC EDGAR, web search wrappers
├── cache/ # SQLite cache
├── prompts/ # prompt templates, kept out of code
└── reports/ # generated Markdown reports

## Setup

```bash
uv sync
cp .env.example .env   # add a free Groq key from console.groq.com
uv run main.py "Tesla" --ticker TSLA
```

## Known limitations

- Free-tier rate limits mean each report takes noticeably longer than a
  single LLM call, but this is a deliberate tradeoff for zero cost
- Web-search-sourced facts don't carry reliable timestamps, so research
  quality on time-sensitive questions (e.g. recent risks/news) can vary
  run to run
- SEC filings are currently referenced by URL only; deeper filing-text
  extraction (e.g. pulling the actual Risk Factors section) is a future
  improvement that could be implemented
