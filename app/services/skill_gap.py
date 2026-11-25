def _get_skill_name(skill):
    """Get a cleaned skill name from a Skill object or string."""
    if isinstance(skill, str):
        name = skill
    else:
        name = getattr(skill, "skill_name", "")

    return name.strip() if isinstance(name, str) else ""


def _unique_skill_names(skills):
    """Remove empty names and duplicates, preserving first occurrence."""
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


def analyze_skill_gaps(student_profile, internships):
    """
    Rank missing skills by how frequently they appear in internships.

    Each skill is counted at most once per internship.
    Skills already present in the student's profile are excluded.
    Results are sorted by frequency (highest first), then alphabetically.
    """
    student_skills = {
        name.casefold()
        for name in _unique_skill_names(
            getattr(student_profile, "skills", [])
        )
    }

    skill_counts = {}
    skill_display_names = {}

    for internship in internships or []:
        required_skills = _unique_skill_names(
            getattr(internship, "skills", [])
        )

        # Fall back to the text field for older records.
        if not required_skills:
            required_skills_text = getattr(
                internship, "required_skills", ""
            )

            if isinstance(required_skills_text, str):
                required_skills = _unique_skill_names(
                    required_skills_text.split(",")
                )

        # Count a skill only once for this internship.
        for skill_name in required_skills:
            normalized_name = skill_name.casefold()

            if normalized_name in student_skills:
                continue

            skill_display_names.setdefault(
                normalized_name,
                skill_name
            )

        missing_internship_skills = {
            name.casefold()
            for name in required_skills
            if name.casefold() not in student_skills
        }

        for normalized_name in missing_internship_skills:
            skill_counts[normalized_name] = (
                skill_counts.get(normalized_name, 0) + 1
            )

    ranked_gaps = sorted(
        skill_counts.items(),
        key=lambda item: (-item[1], item[0])
    )

    return [
        {
            "skill_name": skill_display_names[normalized_name],
            "internship_count": count
        }
        for normalized_name, count in ranked_gaps
    ]