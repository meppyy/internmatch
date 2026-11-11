import re

# Canonical skill names mapped to their recognized aliases.
SKILL_ALIASES = {
    "Python": ["Python"],
    "Flask": ["Flask"],
    "JavaScript": ["JavaScript"],
    "TypeScript": ["TypeScript"],
    "Java": ["Java"],
    "C++": ["C++"],
    "C#": ["C#"],
    "C": ["C"],
    "SQL": ["SQL"],
    "HTML": ["HTML"],
    "CSS": ["CSS"],
    "React": ["React", "React.js"],
    "Node.js": ["Node.js", "NodeJS"],
    "Django": ["Django"],
    "FastAPI": ["FastAPI"],
    "REST APIs": [
        "REST APIs",
        "REST API",
        "RESTful APIs",
        "RESTful API"
    ],
    "scikit-learn": [
        "scikit-learn",
        "scikit learn",
        "sklearn"
    ],
    "Pandas": ["Pandas"],
    "NumPy": ["NumPy", "Numpy"],
    "Matplotlib": ["Matplotlib"],
    "Seaborn": ["Seaborn"],
    "TensorFlow": ["TensorFlow"],
    "PyTorch": ["PyTorch"],
    "Git": ["Git"],
    "GitHub": ["GitHub"],
    "Docker": ["Docker"],
    "Kubernetes": ["Kubernetes"],
    "AWS": ["AWS", "Amazon Web Services"],
    "Azure": ["Microsoft Azure", "Azure"],
    "Google Cloud": ["Google Cloud", "GCP"],
    "Linux": ["Linux"],
    "MySQL": ["MySQL"],
    "PostgreSQL": ["PostgreSQL"],
    "MongoDB": ["MongoDB"],
    "Power BI": ["Power BI"],
    "Tableau": ["Tableau"],
    "Excel": ["Microsoft Excel", "Excel"],
}


def _compile_alias(alias):
    """Compile an alias with flexible whitespace and word boundaries."""
    escaped_alias = re.escape(alias)
    escaped_alias = escaped_alias.replace(r"\ ", r"\s+")

    return re.compile(
        rf"(?<!\w){escaped_alias}(?!\w)",
        re.IGNORECASE
    )


def extract_skills(resume_text):
    """
    Extract known skills from resume text.

    Returns canonical skill names in order of first appearance.
    Matching is case-insensitive and duplicate aliases are removed.
    """

    if not isinstance(resume_text, str) or not resume_text.strip():
        return []

    matches = []

    for position, (canonical_name, aliases) in enumerate(
        SKILL_ALIASES.items()
    ):
        earliest_match = None

        for alias in aliases:
            pattern = _compile_alias(alias)

            for match in pattern.finditer(resume_text):
                if (
                    earliest_match is None
                    or match.start() < earliest_match.start()
                ):
                    earliest_match = match

        if earliest_match:
            matches.append((
                earliest_match.start(),
                -len(earliest_match.group()),
                position,
                canonical_name
            ))

    matches.sort()

    return [
        match[3]
        for match in matches
    ]