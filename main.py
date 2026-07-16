import argparse
from datetime import date

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

import config
from agent import planner, researcher, summarizer, synthesizer

console = Console()


def run(topic: str, ticker: str) -> str:
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task(description="Planning research questions...", total=None)
        questions = planner.plan(topic)
        progress.update(task, description=f"Planned {len(questions)} sub-questions")

        notes = []
        for q in questions:
            progress.update(task, description=f"Researching: {q[:60]}...")
            raw = researcher.research(ticker, q)

            progress.update(task, description=f"Summarizing: {q[:60]}...")
            note = summarizer.summarize(q, raw["data"])
            notes.append((q, note))

        progress.update(task, description="Synthesizing final report...")
        report = synthesizer.synthesize(topic, notes)

    return report


def main():
    parser = argparse.ArgumentParser(description="Free deep-research investment agent")
    parser.add_argument("topic", help="Company name or research topic")
    parser.add_argument("--ticker", help="Stock ticker (defaults to the topic itself)", default=None)
    args = parser.parse_args()

    ticker = args.ticker or args.topic
    report = run(args.topic, ticker)

    out_path = config.REPORTS_DIR / f"{ticker.upper()}_{date.today().isoformat()}.md"
    out_path.write_text(report)

    console.print(f"\n[bold green]Report saved to:[/bold green] {out_path}\n")
    console.print(report)


if __name__ == "__main__":
    main()