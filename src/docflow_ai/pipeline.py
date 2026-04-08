from __future__ import annotations

import asyncio
from dataclasses import dataclass

from docflow_ai.extractors import RegexExtractor
from docflow_ai.matching import CandidateJobMatcher
from docflow_ai.models import MatchResult


@dataclass(slots=True)
class PipelineStats:
    processed_pairs: int
    avg_score: float


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

    async def process_batch(self, cv_docs: list[str], job_docs: list[str]) -> tuple[list[dict[str, str | float]], PipelineStats]:
        if len(cv_docs) != len(job_docs):
            msg = "cv_docs and job_docs must have same length"
            raise ValueError(msg)

        tasks = [self.process_pair(cv, job) for cv, job in zip(cv_docs, job_docs, strict=True)]
        results = await asyncio.gather(*tasks)

        rows = [
            {
                "candidate": r.candidate.name or "",
                "job_title": r.job.title or "",
                "score": r.score,
                "level": r.level,
                "missing_skills": ", ".join(r.missing_skills),
            }
            for r in results
        ]
        avg = sum(r["score"] for r in rows) / len(rows) if rows else 0.0
        stats = PipelineStats(processed_pairs=len(results), avg_score=float(avg))
        return rows, stats
