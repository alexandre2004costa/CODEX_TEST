from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CV x Job extraction/matching pipeline")
    parser.add_argument("--cv-dir", type=Path, default=Path("data/cv"))
    parser.add_argument("--job-dir", type=Path, default=Path("data/jobs"))
    parser.add_argument("--mode", choices=["paired", "cross"], default="paired")
    parser.add_argument("--top-k", type=int, default=None)
    parser.add_argument("--bootstrap-data", action="store_true", help="Download extra CV/job samples from internet")
    args = parser.parse_args()

    if args.bootstrap_data:
        added_cv, added_job = bootstrap_dataset(args.cv_dir, args.job_dir)
        print(f"Downloaded {added_cv} CV docs and {added_job} job docs into local data folders.")

    asyncio.run(run(args.cv_dir, args.job_dir, mode=args.mode, top_k=args.top_k))


if __name__ == "__main__":
    main()
