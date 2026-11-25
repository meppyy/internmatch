def _get_skill_name(skill):
    """Return a cleaned skill name from a Skill object or string."""
    if isinstance(skill, str):
        name = skill
    else:
        name = getattr(skill, "skill_name", "")

    return name.strip() if isinstance(name, str) else ""


def _unique_skill_names(skills):
    """Remove empty names and duplicates while preserving order."""
    unique_names = []
    seen = set()

    for skill in skills or []:
        name = _get_skill_name(skill)

        if not name:
            continue

        normalized_name = name.casefold()

        if normalized_name not in seen:
            seen.add(normalized_name)
            unique_names.append(name)

    return unique_names


def calculate_skill_match(student_profile, internship):
    """
    Compare a student's skills with an internship's requirements.

    The internship Skill relationship is the primary source.
    The required_skills text field is used as a fallback when
    the relationship has no skills.

    Returns the match percentage, matched skills, missing skills,
    complete required skill list, and a human-readable explanation.
    """
    student_skills = _unique_skill_names(
        getattr(student_profile, "skills", [])
    )

    required_skills = _unique_skill_names(
        getattr(internship, "skills", [])
    )

    # Support older records where requirements exist only as text.
    if not required_skills:
        required_skills_text = getattr(
            internship, "required_skills", ""
        )

        if isinstance(required_skills_text, str):
            required_skills = _unique_skill_names(
                required_skills_text.split(",")
            )

    student_skill_keys = {
        skill.casefold() for skill in student_skills
    }

    matched_skills = [
        skill for skill in required_skills
        if skill.casefold() in student_skill_keys
    ]

    missing_skills = [
        skill for skill in required_skills
        if skill.casefold() not in student_skill_keys
    ]

    if not required_skills:
        score = None
        explanation = "No required skills have been specified."
    else:
        score = round(
            len(matched_skills) / len(required_skills) * 100
        )

        explanation = (
            f"Matched {len(matched_skills)} of "
            f"{len(required_skills)} required skills "
            f"({score}%)."
        )

    return {
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "required_skills": required_skills,
        "explanation": explanation
    }