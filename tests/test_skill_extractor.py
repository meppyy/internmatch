import pytest


def test_extracts_known_skills_from_resume_text():
    from app.services.skill_extractor import extract_skills

    resume_text = (
        "Developed applications using PYTHON and Flask. "
        "Used scikit-learn for machine learning and "
        "built RESTful APIs with JavaScript."
    )

    result = extract_skills(resume_text)

    assert result == [
        "Python",
        "Flask",
        "scikit-learn",
        "REST APIs",
        "JavaScript"
    ]


def test_skill_extraction_is_case_insensitive_and_deduplicates():
    from app.services.skill_extractor import extract_skills

    resume_text = (
        "Python, PYTHON, python, Flask, FLASK, sklearn."
    )

    result = extract_skills(resume_text)

    assert result == [
        "Python",
        "Flask",
        "scikit-learn"
    ]


def test_skill_aliases_map_to_canonical_names():
    from app.services.skill_extractor import extract_skills

    resume_text = (
        "Experience with sklearn, scikit learn, "
        "and scikit-learn."
    )

    result = extract_skills(resume_text)

    assert result == ["scikit-learn"]


def test_does_not_match_skills_inside_larger_words():
    from app.services.skill_extractor import extract_skills

    resume_text = (
        "JavaScript development and reactive user interfaces."
    )

    result = extract_skills(resume_text)

    assert result == ["JavaScript"]


def test_returns_empty_list_for_empty_resume_text():
    from app.services.skill_extractor import extract_skills

    assert extract_skills("") == []
    assert extract_skills(None) == []
    assert extract_skills("   ") == []