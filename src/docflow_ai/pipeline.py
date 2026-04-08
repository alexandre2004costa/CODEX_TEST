from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Literal

from docflow_ai.extractors import RegexExtractor
from docflow_ai.matching import CandidateJobMatcher
from docflow_ai.models import MatchResult


@dataclass(slots=True)
class PipelineStats:
    processed_pairs: int
    avg_score: float
    high_fit_ratio: float


class DocumentPipeline:
    """Asynchronous pipeline emulating production-scale CV x Job matching."""

    def __init__(self) -> None:
        self.extractor = RegexExtractor()
        self.matcher = CandidateJobMatcher()

    async def process_pair(self, cv_text: str, job_text: str) -> MatchResult:
        candidate = self.extractor.extract_candidate(cv_text)
        job = self.extractor.extract_job(job_text)
        await asyncio.sleep(0)
        return self.matcher.score(candidate, job)

    async def process_batch(
        self,
        cv_docs: list[str],
        job_docs: list[str],
        mode: Literal["paired", "cross"] = "paired",
        top_k: int | None = None,
    ) -> tuple[list[dict[str, str | float]], PipelineStats]:
        if mode == "paired" and len(cv_docs) != len(job_docs):
            msg = "cv_docs and job_docs must have same length in paired mode"
            raise ValueError(msg)

        if mode == "paired":
            tasks = [self.process_pair(cv, job) for cv, job in zip(cv_docs, job_docs, strict=True)]
        else:
            tasks = [self.process_pair(cv, job) for cv in cv_docs for job in job_docs]

        results = await asyncio.gather(*tasks)
        if top_k is not None:
            results = sorted(results, key=lambda r: r.score, reverse=True)[:top_k]

        rows = [
            {
                "candidate": r.candidate.name or "",
                "job_title": r.job.title or "",
                "score": r.score,
                "level": r.level,
                "skill_coverage": r.skill_coverage,
                "experience_gap": r.experience_gap,
                "matched_skills": ", ".join(r.matched_skills),
                "missing_skills": ", ".join(r.missing_skills),
            }
            for r in results
        ]
        avg = sum(r["score"] for r in rows) / len(rows) if rows else 0.0
        high_fit_count = sum(1 for r in rows if r["level"] == "high")
        stats = PipelineStats(
            processed_pairs=len(results),
            avg_score=float(avg),
            high_fit_ratio=(high_fit_count / len(rows)) if rows else 0.0,
        )
        return rows, stats
