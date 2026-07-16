import json

import config
from agent.llm import invoke


def summarize(question: str, raw_data) -> str:
    """
    Condense raw tool output into a few bullet points. Uses the fast
    model
    """
    template = (config.PROMPTS_DIR / "summarizer.txt").read_text()
    prompt = template.format(
        question=question,
        raw_data=json.dumps(raw_data, indent=2, default=str)[:4000],  # keep payload small
    )
    return invoke(prompt, smart=False)