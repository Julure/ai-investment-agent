import config
from agent.llm import invoke


def synthesize(topic: str, notes: list[tuple[str, str]]) -> str:
    """
    Combine all sub-question notes into one structured report. Uses the
    smart model with deep reasoning,only runs once per research session."""
    template = (config.PROMPTS_DIR / "synthesizer.txt").read_text()

    notes_block = "\n\n".join(f"### {q}\n{note}" for q, note in notes)
    prompt = template.format(topic=topic, notes=notes_block)

    return invoke(prompt, smart=True)