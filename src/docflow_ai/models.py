from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(slots=True)
class CandidateProfile:
    name: str | None = None
    email: str | None = None
    years_experience: float = 0.0
    skills: list[str] = field(default_factory=list)


@dataclass(slots=True)
class JobProfile:
    title: str | None = None
    company: str | None = None
    min_years_experience: float = 0.0
    required_skills: list[str] = field(default_factory=list)


@dataclass(slots=True)
class MatchResult:
    candidate: CandidateProfile
    job: JobProfile
    score: float
    level: Literal["low", "medium", "high"]
    missing_skills: list[str] = field(default_factory=list)
    matched_skills: list[str] = field(default_factory=list)
    skill_coverage: float = 0.0
    experience_gap: float = 0.0
