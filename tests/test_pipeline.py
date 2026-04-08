import asyncio

from docflow_ai.pipeline import DocumentPipeline


def test_process_batch_returns_scores() -> None:
    pipeline = DocumentPipeline()
    cvs = [
        "John Doe\nEmail: john@x.com\n4 years experience. Skills: Python, NLP, LLM, SQL, Docker",
        "Mary Jane\nEmail: mary@x.com\n1 years experience. Skills: Python, SQL",
    ]
    jobs = [
        "AI Engineer\nCompany: A\nNeed 2 years experience. Must have: Python, NLP, LLM, Docker",
        "ML Engineer\nCompany: B\nNeed 2 years experience. Must have: Python, SQL, NLP",
    ]

    frame, stats = asyncio.run(pipeline.process_batch(cvs, jobs))

    assert len(frame) == 2
    assert stats.processed_pairs == 2
    assert 0 <= stats.avg_score <= 1
    assert "skill_coverage" in frame[0]


def test_cross_mode_and_top_k() -> None:
    pipeline = DocumentPipeline()
    cvs = [
        "Alex Smith\nEmail: alex@x.com\n5 yrs experience. Skills: Py, Natural Language Processing, Docker, AWS",
        "Rita Jones\nEmail: rita@x.com\n2 years experience. Skills: SQL, ML",
    ]
    jobs = [
        "NLP Engineer\nCompany: C\nMinimum 3 years experience. Must have: Python, NLP, Docker",
        "Data Engineer\nCompany: D\nNeed 2 years experience. Must have: SQL, Spark",
    ]

    frame, stats = asyncio.run(pipeline.process_batch(cvs, jobs, mode="cross", top_k=2))

    assert len(frame) == 2
    assert stats.processed_pairs == 2
    assert frame[0]["score"] >= frame[1]["score"]
    assert "python" in frame[0]["matched_skills"]
