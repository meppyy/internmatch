from types import SimpleNamespace


def make_profile(skill_names):
    return SimpleNamespace(
        skills=[
            SimpleNamespace(skill_name=name)
            for name in skill_names
        ]
    )


def make_internship(skill_names=None, required_skills=None):
    return SimpleNamespace(
        skills=[
            SimpleNamespace(skill_name=name)
            for name in (skill_names or [])
        ],
        required_skills=required_skills
    )


def test_calculates_match_percentage_and_missing_skills():
    from app.services.skill_matching import calculate_skill_match

    student = make_profile(["Python", "SQL", "Git"])
    internship = make_internship(
        ["Python", "SQL", "Flask", "JavaScript"]
    )

    result = calculate_skill_match(student, internship)

    assert result["score"] == 50
    assert result["matched_skills"] == ["Python", "SQL"]
    assert result["missing_skills"] == ["Flask", "JavaScript"]
    assert result["required_skills"] == [
        "Python", "SQL", "Flask", "JavaScript"
    ]


def test_matching_is_case_insensitive_and_ignores_duplicates():
    from app.services.skill_matching import calculate_skill_match

    student = make_profile(["python", "PYTHON", "flask"])
    internship = make_internship(
        ["Python", "Flask", "SQL", "Python"]
    )

    result = calculate_skill_match(student, internship)

    assert result["score"] == 67
    assert result["matched_skills"] == ["Python", "Flask"]
    assert result["missing_skills"] == ["SQL"]


def test_returns_zero_when_student_has_none_of_the_required_skills():
    from app.services.skill_matching import calculate_skill_match

    student = make_profile(["Java"])
    internship = make_internship(["Python", "SQL"])

    result = calculate_skill_match(student, internship)

    assert result["score"] == 0
    assert result["matched_skills"] == []
    assert result["missing_skills"] == ["Python", "SQL"]


def test_handles_internship_without_required_skills():
    from app.services.skill_matching import calculate_skill_match

    student = make_profile(["Python"])
    internship = make_internship()

    result = calculate_skill_match(student, internship)

    assert result["score"] is None
    assert result["matched_skills"] == []
    assert result["missing_skills"] == []
    assert result["required_skills"] == []


def test_uses_required_skills_text_when_relationship_is_empty():
    from app.services.skill_matching import calculate_skill_match

    student = make_profile(["Python", "Git"])
    internship = make_internship(
        required_skills="Python, SQL, Git"
    )

    result = calculate_skill_match(student, internship)

    assert result["score"] == 67
    assert result["matched_skills"] == ["Python", "Git"]
    assert result["missing_skills"] == ["SQL"]