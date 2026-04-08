# DocFlow AI — CV & Job Ad Intelligence Pipeline

This portfolio project demonstrates **Python + NLP + LLM-oriented information extraction** for CVs and job ads, followed by **candidate-job matching**. It is designed to map to a Junior AI Engineer role focused on high-volume document processing.

## Why this fits the opportunity

- **Python engineering**: modular package, typing, dataclass schemas, CLI entrypoint, unit tests.
- **NLP/LLM use-case**: extract structured entities from unstructured CV/job text (skills, experience, metadata).
- **Pipeline mindset**: asynchronous batch processing (`asyncio.gather`) to emulate production throughput.
- **Optimization mindset**: deterministic regex extractor as a fast baseline before expensive LLM calls.
- **ML foundations**: explainable scoring model combining skill coverage + experience gap + bonus signals.

## Standout upgrades in this version

- **Skill normalization layer** with aliases (e.g., `Py -> python`, `k8s -> kubernetes`, `natural language processing -> nlp`) for more realistic document parsing.
- **Explainable matching metrics** per candidate/job pair:
  - fit score + fit level,
  - skill coverage,
  - experience gap,
  - matched and missing skills.
- **Cross-matching mode** to evaluate every CV against every job ad (N×M), plus `--top-k` shortlist support.
- **Recruiter-friendly KPI**: high-fit ratio in pipeline stats.

## Architecture

```text
Documents (CVs + Job Ads)
    -> Extraction Layer (RegexExtractor with alias normalization; LLM-ready design)
    -> Canonical Schemas (CandidateProfile, JobProfile)
    -> Matching Layer (explainable fit + coverage + gap + missing skills)
    -> Batch Pipeline (async processing + cross-match ranking)
```

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest

# Classic 1:1 pairing by file order
python -m docflow_ai.cli --cv-dir data/cv --job-dir data/jobs --mode paired

# Portfolio-ready shortlist across all combinations
python -m docflow_ai.cli --cv-dir data/cv --job-dir data/jobs --mode cross --top-k 5
```

## Example output

Per candidate/job pair:

- `score` (`0.0 - 1.0`) and `level` (`low`, `medium`, `high`)
- `skill_coverage` (how much of required skill set is covered)
- `experience_gap` (years missing vs required threshold)
- `matched_skills` and `missing_skills` (actionable recruiter feedback)

Pipeline summary:

- processed pairs
- average score
- high-fit ratio

## How to present this in interviews

1. Explain this as a **baseline production architecture**:
   - deterministic extraction for speed/cost,
   - optional LLM fallback for hard documents.
2. Demo the **cross-match + top-k shortlist** flow as a realistic recruiter scenario.
3. Propose scaling steps:
   - queue-based ingestion (Kafka/SQS),
   - vector retrieval for semantic skill normalization,
   - monitoring (latency, extraction quality, drift).
4. Show business impact:
   - faster screening,
   - consistent CV-job matching,
   - transparent fit explanations for recruiters.

## Next improvements

- Add an LLM adapter (`OpenAI` or local model) with JSON-constrained outputs.
- Add evaluation set and extraction precision/recall dashboard.
- Deploy API with FastAPI and background workers.
