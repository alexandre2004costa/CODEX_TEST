from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import Callable
from typing import Literal

from docflow_ai.bootstrap import bootstrap_dataset
from docflow_ai.pipeline import DocumentPipeline


def load_docs(folder: Path) -> list[str]:
    return [p.read_text(encoding="utf-8") for p in sorted(folder.glob("*.txt"))]


def print_table(rows: list[dict[str, str | float]]) -> None:
    headers = [
        "candidate",
        "job_title",
        "score",
        "level",
        "skill_coverage",
        "experience_gap",
        "matched_skills",
        "missing_skills",
    ]
    line = " | ".join(headers)
    print(line)
    print("-" * len(line))
    for row in rows:
        print(" | ".join(str(row[h]) for h in headers))


async def run(cv_dir: Path, job_dir: Path, mode: Literal["paired", "cross"], top_k: int | None) -> None:
    pipeline = DocumentPipeline()
    cvs = load_docs(cv_dir)
    jobs = load_docs(job_dir)
    rows, stats = await pipeline.process_batch(cvs, jobs, mode=mode, top_k=top_k)
    print_table(rows)
    print(
        "\nProcessed pairs: "
        f"{stats.processed_pairs} | Avg score: {stats.avg_score:.3f} | High fit ratio: {stats.high_fit_ratio:.2%}"
    )


def _prompt_mode(input_fn: Callable[[str], str] | None = None) -> Literal["paired", "cross"]:
    if input_fn is None:
        input_fn = input
    while True:
        selected = input_fn("Select mode ([p]aired / [c]ross): ").strip().lower()
        if selected in {"p", "paired"}:
            return "paired"
        if selected in {"c", "cross"}:
            return "cross"
        print("Invalid mode. Please type 'p'/'paired' or 'c'/'cross'.")


def _prompt_top_k(input_fn: Callable[[str], str] | None = None) -> int | None:
    if input_fn is None:
        input_fn = input
    while True:
        selected = input_fn("Top-k results (blank for all): ").strip()
        if not selected:
            return None
        if selected.isdigit() and int(selected) > 0:
            return int(selected)
        print("Invalid top-k. Enter a positive number or leave blank.")


def _prompt_yes_no(question: str, input_fn: Callable[[str], str] | None = None) -> bool:
    if input_fn is None:
        input_fn = input
    while True:
        selected = input_fn(f"{question} [y/n]: ").strip().lower()
        if selected in {"y", "yes"}:
            return True
        if selected in {"n", "no"}:
            return False
        print("Please answer with 'y'/'yes' or 'n'/'no'.")


def interactive_main(default_cv_dir: Path, default_job_dir: Path) -> None:
    print("DocFlow AI interactive mode")
    print("Press Ctrl+C at any time to exit.\n")
    cv_dir = default_cv_dir
    job_dir = default_job_dir

    while True:
        try:
            cv_input = input(f"CV directory [{cv_dir}]: ").strip()
            if cv_input:
                cv_dir = Path(cv_input)
            job_input = input(f"Job directory [{job_dir}]: ").strip()
            if job_input:
                job_dir = Path(job_input)
            if _prompt_yes_no("Bootstrap extra internet samples before running?"):
                added_cv, added_job = bootstrap_dataset(cv_dir, job_dir)
                print(f"Downloaded {added_cv} CV docs and {added_job} job docs into local data folders.")

            mode = _prompt_mode()
            top_k = _prompt_top_k() if mode == "cross" else None
            asyncio.run(run(cv_dir, job_dir, mode=mode, top_k=top_k))
            print()
            if not _prompt_yes_no("Run another experiment?"):
                break
            print()
        except KeyboardInterrupt:
            print("\nExiting interactive mode.")
            break


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CV x Job extraction/matching pipeline")
    parser.add_argument("--cv-dir", type=Path, default=Path("data/cv"))
    parser.add_argument("--job-dir", type=Path, default=Path("data/jobs"))
    parser.add_argument("--mode", choices=["paired", "cross"], default="paired")
    parser.add_argument("--top-k", type=int, default=None)
    parser.add_argument("--bootstrap-data", action="store_true", help="Download extra CV/job samples from internet")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive run configuration")
    args = parser.parse_args()

    if args.interactive:
        interactive_main(args.cv_dir, args.job_dir)
        return

    if args.bootstrap_data:
        added_cv, added_job = bootstrap_dataset(args.cv_dir, args.job_dir)
        print(f"Downloaded {added_cv} CV docs and {added_job} job docs into local data folders.")

    asyncio.run(run(args.cv_dir, args.job_dir, mode=args.mode, top_k=args.top_k))


if __name__ == "__main__":
    main()
