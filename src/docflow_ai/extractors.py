from __future__ import annotations

import re
from dataclasses import dataclass

from docflow_ai.models import CandidateProfile, JobProfile

SKILL_ALIASES: dict[str, set[str]] = {
    "python": {"python", "py"},
    "sql": {"sql", "postgres", "mysql", "sqlite"},
    "nlp": {"nlp", "natural language processing"},
    "machine learning": {"machine learning", "ml"},
    "deep learning": {"deep learning", "dl"},
    "pytorch": {"pytorch", "torch"},
    "tensorflow": {"tensorflow", "tf"},
    "docker": {"docker", "containerization"},
    "kubernetes": {"kubernetes", "k8s"},
    "fastapi": {"fastapi"},
    "aws": {"aws", "amazon web services"},
    "gcp": {"gcp", "google cloud"},
    "airflow": {"airflow"},
    "spark": {"spark", "pyspark", "apache spark"},
    "llm": {"llm", "large language model", "large language models", "gpt"},
    "rag": {"rag", "retrieval augmented generation"},
}


@dataclass(slots=True)
class RegexExtractor:
    """Fast baseline extractor for high-throughput document streams."""

    def extract_candidate(self, text: str) -> CandidateProfile:
        normalized = text.lower()
        email = self._extract_email(text)
        years = self._extract_years(normalized)
        skills = self._extract_skills(normalized)
        name = self._extract_name(text)
        return CandidateProfile(name=name, email=email, years_experience=years, skills=skills)

    def extract_job(self, text: str) -> JobProfile:
        normalized = text.lower()
        years = self._extract_years(normalized)
        skills = self._extract_skills(normalized)
        title = self._extract_title(text)
        company = self._extract_company(text)
        return JobProfile(
            title=title,
            company=company,
            min_years_experience=years,
            required_skills=skills,
        )

    @staticmethod
    def _extract_email(text: str) -> str | None:
        match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        return match.group(0) if match else None

    @staticmethod
    def _extract_years(text: str) -> float:
        patterns = [
            r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)",
            r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)",
            r"(?:minimum|min)\s*(\d+(?:\.\d+)?)\s*(?:years|yrs)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return float(match.group(1))
        return 0.0

    @staticmethod
    def _extract_skills(text: str) -> list[str]:
        extracted: list[str] = []
        for canonical, aliases in SKILL_ALIASES.items():
            if any(alias in text for alias in aliases):
                extracted.append(canonical)
        return sorted(extracted)

    @staticmethod
    def _extract_name(text: str) -> str | None:
        first_line = text.splitlines()[0].strip()
        return first_line if first_line and "@" not in first_line else None

    @staticmethod
    def _extract_title(text: str) -> str | None:
        first_line = text.splitlines()[0].strip()
        return first_line if first_line else None

    @staticmethod
    def _extract_company(text: str) -> str | None:
        match = re.search(r"company\s*[:\-]\s*([^\n]+)", text, flags=re.IGNORECASE)
        return match.group(1).strip() if match else None
