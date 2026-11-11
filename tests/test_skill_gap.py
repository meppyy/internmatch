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


def test_prioritizes_missing_skills_by_listing_frequency():
    from app.services.skill_gap import analyze_skill_gaps

    student = make_profile(["Python"])

    internships = [
        make_internship(["Python", "SQL", "Flask"]),
        make_internship(["SQL", "Flask", "JavaScript"]),
        make_internship(["SQL", "Git"])
    ]

    result = analyze_skill_gaps(student, internships)

    assert result == [
        {"skill_name": "SQL", "internship_count": 3},
        {"skill_name": "Flask", "internship_count": 2},
        {"skill_name": "Git", "internship_count": 1},
        {"skill_name": "JavaScript", "internship_count": 1}
    ]


def test_excludes_skills_already_present_in_student_profile():
    from app.services.skill_gap import analyze_skill_gaps

    student = make_profile(["Python", "SQL"])

    internships = [
        make_internship(["Python", "SQL", "Flask"]),
        make_internship(["Python", "SQL", "Docker"])
    ]

    result = analyze_skill_gaps(student, internships)

    assert result == [
        {"skill_name": "Docker", "internship_count": 1},
        {"skill_name": "Flask", "internship_count": 1}
    ]


def test_counts_each_skill_once_per_internship_case_insensitively():
    from app.services.skill_gap import analyze_skill_gaps

    student = make_profile([])

    internships = [
        make_internship(["Python", "python", "SQL"]),
        make_internship(["PYTHON", "SQL"])
    ]

    result = analyze_skill_gaps(student, internships)

    assert result == [
        {"skill_name": "Python", "internship_count": 2},
        {"skill_name": "SQL", "internship_count": 2}
    ]


def test_returns_empty_list_when_there_are_no_skill_gaps():
    from app.services.skill_gap import analyze_skill_gaps

    student = make_profile(["Python", "SQL"])

    internships = [
        make_internship(["Python", "SQL"]),
        make_internship()
    ]

    result = analyze_skill_gaps(student, internships)

    assert result == []