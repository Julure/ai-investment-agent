import json

import config
from agent.llm import invoke

def _is_flat_scalar_dict(data) -> bool:
    return isinstance(data, dict) and all(
        not isinstance(v, (dict, list)) for v in data.values()
    )


def _humanize_key(key: str) -> str:
    return key.replace("_", " ").capitalize()


def _format_flat_dict(data: dict) -> str:
    """Turn a flat dict straight into bullet points"""
    lines = [
        f"- {_humanize_key(k)}: {v}"
        for k, v in data.items()
        if v is not None and v != ""
    ]
    return "\n".join(lines) if lines else "- No data available for this source."


def summarize(question: str, raw_data) -> str:
    """
    Condense raw tool output into a few bullet points. Uses the fast
    model
    """
    if _is_flat_scalar_dict(raw_data):
        return _format_flat_dict(raw_data)

    template = (config.PROMPTS_DIR / "summarizer.txt").read_text()
    prompt = template.format(
        question=question,
        raw_data=json.dumps(raw_data, indent=2, default=str)[:4000],  # keep payload small
    )
    return invoke(prompt, smart=False)