import re

import config
from agent.llm import invoke


def plan(topic: str) -> list[str]:
    """Generate research sub-questions for a topic. Uses the fast model, no deep reasoning"""
    template = (config.PROMPTS_DIR / "planner.txt").read_text()
    prompt = template.format(topic=topic)
    raw = invoke(prompt, smart=False)

    questions = []
    for line in raw.splitlines():
        line = line.strip()
        cleaned = re.sub(r"^\d+[\.\)]\s*", "", line)
        if cleaned:
            questions.append(cleaned)
    return questions