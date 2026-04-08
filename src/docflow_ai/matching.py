from __future__ import annotations

from difflib import SequenceMatcher

from docflow_ai.models import CandidateProfile, JobProfile, MatchResult


class CandidateJobMatcher:
    """Computes explainable fit score between CV and Job Ad."""

    def score(self, candidate: CandidateProfile, job: JobProfile) -> MatchResult:
        req_skills = set(job.required_skills)
        cand_skills = set(candidate.skills)

        if not req_skills:
            skill_score = 0.5
            missing = []
        else:
            covered = len(req_skills & cand_skills)
            skill_score = covered / len(req_skills)
            missing = sorted(req_skills - cand_skills)

        exp_gap = max(job.min_years_experience - candidate.years_experience, 0)
        exp_score = max(0.0, 1 - exp_gap / 5)

        title_score = 0.0
        if candidate.name and job.title:
            title_score = SequenceMatcher(None, candidate.name.lower(), job.title.lower()).ratio()

        final_score = round(0.65 * skill_score + 0.30 * exp_score + 0.05 * title_score, 3)

        if final_score >= 0.75:
            level = "high"
        elif final_score >= 0.5:
            level = "medium"
        else:
            level = "low"

        return MatchResult(
            candidate=candidate,
            job=job,
            score=final_score,
            level=level,
            missing_skills=missing,
        )
