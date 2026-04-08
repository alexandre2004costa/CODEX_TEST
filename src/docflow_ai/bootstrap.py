from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen


@dataclass(frozen=True, slots=True)
class RemoteSource:
    url: str
    kind: str


REMOTE_SOURCES: tuple[RemoteSource, ...] = (
    RemoteSource(
        url="https://raw.githubusercontent.com/jsonresume/resume-schema/master/sample.resume.json",
        kind="cv_json_resume",
    ),
    RemoteSource(
        url="https://raw.githubusercontent.com/jsonresume/resume-schema/master/sample.job.json",
        kind="job_json_resume",
    ),
    RemoteSource(
        url="https://gist.githubusercontent.com/owainlewis/5fb7905f2e315d61439c/raw/",
        kind="job_text",
    ),
    RemoteSource(
        url="https://gist.githubusercontent.com/thasan4/35da5c4b0fb05fc2f8d2e6da1f1dcf7e/raw/",
        kind="job_text",
    ),
    RemoteSource(
        url="https://raw.githubusercontent.com/posquit0/Awesome-CV/master/examples/resume.tex",
        kind="cv_text",
    ),
    RemoteSource(
        url="https://raw.githubusercontent.com/posquit0/Awesome-CV/master/examples/cv.tex",
        kind="cv_text",
    ),
    RemoteSource(
        url="https://raw.githubusercontent.com/jsonresume/resume-schema/master/README.md",
        kind="cv_text",
    ),
    RemoteSource(
        url="https://raw.githubusercontent.com/remoteintech/remote-jobs/master/README.md",
        kind="job_text",
    ),
)


def _download_text(url: str, timeout_seconds: int = 20) -> str:
    with urlopen(url, timeout=timeout_seconds) as response:
        payload = response.read()
    return payload.decode("utf-8", errors="ignore")


def _years_between(start_date: str) -> int:
    try:
        year = int(start_date.split("-")[0])
    except (TypeError, ValueError, IndexError):
        return 0
    return max(date.today().year - year, 0)


def _resume_json_to_text(payload: dict[str, Any]) -> str:
    basics = payload.get("basics", {})
    name = basics.get("name", "Unknown Candidate")
    email = basics.get("email", "unknown@example.com")

    work_items = payload.get("work", [])
    years = 0
    for item in work_items:
        years = max(years, _years_between(item.get("startDate", "")))

    raw_skills = [skill.get("name", "") for skill in payload.get("skills", [])]
    skills = ", ".join(s for s in raw_skills if s)

    return f"{name}\nEmail: {email}\n{years} years experience. Skills: {skills}"


def _job_json_to_text(payload: dict[str, Any]) -> str:
    title = payload.get("title", "Unknown Role")
    company = payload.get("organization", "Unknown Company")
    years = payload.get("yearsExperience", 0)

    skill_keys = ("skills", "keywords", "qualifications")
    collected: list[str] = []
    for key in skill_keys:
        raw = payload.get(key, [])
        if isinstance(raw, list):
            collected.extend(str(item) for item in raw)

    skills = ", ".join(collected)
    return f"{title}\nCompany: {company}\nNeed {years} years experience. Must have: {skills}"


def _plain_text_to_doc(text: str, fallback_title: str, source_url: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    snippet = compact[:1800]
    return f"{fallback_title}\nSource: {source_url}\n{snippet}"


def bootstrap_dataset(cv_dir: Path, job_dir: Path, cv_target: int = 6, job_target: int = 6) -> tuple[int, int]:
    cv_dir.mkdir(parents=True, exist_ok=True)
    job_dir.mkdir(parents=True, exist_ok=True)

    next_cv_idx = len(list(cv_dir.glob("cv_*.txt"))) + 1
    next_job_idx = len(list(job_dir.glob("job_*.txt"))) + 1
    added_cv = 0
    added_job = 0

    for source in REMOTE_SOURCES:
        if added_cv >= cv_target and added_job >= job_target:
            break

        try:
            raw = _download_text(source.url)
        except URLError:
            continue

        if source.kind == "cv_json_resume" and added_cv < cv_target:
            text = f"{_resume_json_to_text(json.loads(raw))}\nSource: {source.url}"
            out = cv_dir / f"cv_{next_cv_idx}.txt"
            out.write_text(text, encoding="utf-8")
            next_cv_idx += 1
            added_cv += 1
        elif source.kind == "job_json_resume" and added_job < job_target:
            text = f"{_job_json_to_text(json.loads(raw))}\nSource: {source.url}"
            out = job_dir / f"job_{next_job_idx}.txt"
            out.write_text(text, encoding="utf-8")
            next_job_idx += 1
            added_job += 1
        elif source.kind == "cv_text" and added_cv < cv_target:
            text = _plain_text_to_doc(raw, "Internet Resume Sample", source.url)
            out = cv_dir / f"cv_{next_cv_idx}.txt"
            out.write_text(text, encoding="utf-8")
            next_cv_idx += 1
            added_cv += 1
        elif source.kind == "job_text" and added_job < job_target:
            text = _plain_text_to_doc(raw, "Internet Job Description Sample", source.url)
            out = job_dir / f"job_{next_job_idx}.txt"
            out.write_text(text, encoding="utf-8")
            next_job_idx += 1
            added_job += 1

    return added_cv, added_job
