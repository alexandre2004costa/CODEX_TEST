from docflow_ai.bootstrap import _job_json_to_text, _resume_json_to_text


def test_resume_json_to_text_formats_expected_fields() -> None:
    payload = {
        "basics": {"name": "Jane Doe", "email": "jane@example.com"},
        "work": [{"startDate": "2020-01-01"}],
        "skills": [{"name": "Python"}, {"name": "NLP"}],
    }

    doc = _resume_json_to_text(payload)

    assert "Jane Doe" in doc
    assert "jane@example.com" in doc
    assert "years experience" in doc
    assert "Python, NLP" in doc


def test_job_json_to_text_formats_expected_fields() -> None:
    payload = {
        "title": "ML Engineer",
        "organization": "Acme AI",
        "yearsExperience": 3,
        "skills": ["Python", "SQL"],
        "keywords": ["NLP"],
    }

    doc = _job_json_to_text(payload)

    assert "ML Engineer" in doc
    assert "Acme AI" in doc
    assert "Need 3 years experience" in doc
    assert "Python" in doc and "NLP" in doc
