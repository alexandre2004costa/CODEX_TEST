from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from docflow_ai.pipeline import DocumentPipeline


def load_docs(folder: Path) -> list[str]:
    return [p.read_text(encoding="utf-8") for p in sorted(folder.glob("*.txt"))]


def print_table(rows: list[dict[str, str | float]]) -> None:
    headers = ["candidate", "job_title", "score", "level", "missing_skills"]
    line = " | ".join(headers)
    print(line)
    print("-" * len(line))
    for row in rows:
        print(" | ".join(str(row[h]) for h in headers))


async def run(cv_dir: Path, job_dir: Path) -> None:
    pipeline = DocumentPipeline()
    cvs = load_docs(cv_dir)
    jobs = load_docs(job_dir)
    rows, stats = await pipeline.process_batch(cvs, jobs)
    print_table(rows)
    print(f"\nProcessed pairs: {stats.processed_pairs} | Avg score: {stats.avg_score:.3f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CV x Job extraction/matching pipeline")
    parser.add_argument("--cv-dir", type=Path, default=Path("data/cv"))
    parser.add_argument("--job-dir", type=Path, default=Path("data/jobs"))
    args = parser.parse_args()
    asyncio.run(run(args.cv_dir, args.job_dir))


if __name__ == "__main__":
    main()
