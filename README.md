# DocFlow AI — CV & Job Ad Intelligence Pipeline

This portfolio project demonstrates **Python + NLP + LLM-oriented information extraction** for CVs and job ads, followed by **candidate-job matching**. It is designed to map to a Junior AI Engineer role focused on high-volume document processing.

## Why this fits the opportunity

- **Python engineering**: modular package, typing, dataclass schemas, CLI entrypoint, unit tests.
- **NLP/LLM use-case**: extract structured entities from unstructured CV/job text (skills, experience, metadata).
- **Pipeline mindset**: asynchronous batch processing (`asyncio.gather`) to emulate production throughput.
- **Optimization mindset**: deterministic regex extractor as a fast baseline before expensive LLM calls.
- **ML foundations**: explainable scoring model combining skill coverage + experience gap.

## Architecture

```text
Documents (CVs + Job Ads)
    -> Extraction Layer (RegexExtractor; LLM-ready design)
    -> Canonical Schemas (CandidateProfile, JobProfile)
    -> Matching Layer (scored fit + missing skills)
    -> Batch Pipeline (async processing + tabular output)
```

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
python -m docflow_ai.cli --cv-dir data/cv --job-dir data/jobs
```

## Example output

- Per candidate/job pair:
  - fit score (`0.0 - 1.0`)
  - fit level (`low`, `medium`, `high`)
  - missing skills for actionable feedback

## How to present this in interviews

1. Explain this as a **baseline production architecture**:
   - deterministic extraction for speed/cost
   - optional LLM fallback for hard documents.
2. Propose scaling steps:
   - queue-based ingestion (Kafka/SQS),
   - vector retrieval for semantic skill normalization,
   - monitoring (latency, extraction quality, drift).
3. Show business impact:
   - faster screening,
   - consistent CV-job matching,
   - transparent fit explanations for recruiters.

## Next improvements

- Add an LLM adapter (`OpenAI` or local model) with JSON-constrained outputs.
- Add evaluation set and extraction precision/recall dashboard.
- Deploy API with FastAPI and background workers.
