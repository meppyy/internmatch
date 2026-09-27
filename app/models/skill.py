from ..extensions import db


student_skills = db.Table(
    "student_skills",
    db.Column(
        "student_id",
        db.Integer,
        db.ForeignKey("student_profiles.student_id"),
        primary_key=True
    ),
    db.Column(
        "skill_id",
        db.Integer,
        db.ForeignKey("skills.skill_id"),
        primary_key=True
    )
)


internship_skills = db.Table(
    "internship_skills",
    db.Column(
        "internship_id",
        db.Integer,
        db.ForeignKey("internships.internship_id"),
        primary_key=True
    ),
    db.Column(
        "skill_id",
        db.Integer,
        db.ForeignKey("skills.skill_id"),
        primary_key=True
    )
)


class Skill(db.Model):
    __tablename__ = "skills"

    skill_id = db.Column(db.Integer, primary_key=True)

    skill_name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    students = db.relationship(
        "StudentProfile",
        secondary=student_skills,
        back_populates="skills"
    )

    internships = db.relationship(
        "Internship",
        secondary=internship_skills,
        back_populates="skills"
    )