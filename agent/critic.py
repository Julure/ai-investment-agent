import re
import config
from agent.llm import invoke


def review(topic: str, notes: list[tuple[str, str]], already_asked: list[str]) -> list[str]:

    "Reviews current rearch notes and decides if follow up research is needed if yes returns follow up sub-questions if it is enough it returns an empty list, does not use deep resoning"

    template = (config.PROMPTS_DIR / "critic.txt").read_text()
    notes_block = "\n\n".join(f"### {q}\n{note}" for q, note in notes)
    prompt = template.format(
        topic=topic,
        notes=notes_block,
        already_asked="\n".join(f"- {q}" for q in already_asked),
    )
    raw = invoke(prompt, smart=False)

    if raw.strip().upper().startswith("DONE"):
        return []

    questions = []
    for line in raw.splitlines():
        line = line.strip()
        cleaned = re.sub(r"^[-\d\.\)]+\s*", "", line)
        if cleaned and cleaned.upper() != "DONE":
            questions.append(cleaned)
    return questions