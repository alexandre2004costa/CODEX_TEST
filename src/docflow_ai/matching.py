from __future__ import annotations

from docflow_ai.models import CandidateProfile, JobProfile, MatchResult


class CandidateJobMatcher:
    """Computes explainable fit score between CV and Job Ad."""

    def score(self, candidate: CandidateProfile, job: JobProfile) -> MatchResult:
        req_skills = set(job.required_skills)
        cand_skills = set(candidate.skills)

        if not req_skills:
            skill_score = 0.5
            missing: list[str] = []
            matched: list[str] = []
        else:
            matched_set = req_skills & cand_skills
            matched = sorted(matched_set)
            missing = sorted(req_skills - cand_skills)
            skill_score = len(matched_set) / len(req_skills)

        extra_skills = max(len(cand_skills - req_skills), 0)
        extra_bonus = min(extra_skills * 0.03, 0.12)

        exp_gap = max(job.min_years_experience - candidate.years_experience, 0)
        exp_score = max(0.0, 1 - exp_gap / 5)

        final_score = round(min(1.0, 0.70 * skill_score + 0.25 * exp_score + 0.05 * extra_bonus), 3)

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
            matched_skills=matched,
            skill_coverage=round(skill_score, 3),
            experience_gap=round(exp_gap, 2),
        )
