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
