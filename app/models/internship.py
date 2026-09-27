from datetime import datetime
from .skill import internship_skills

from ..extensions import db


class Internship(db.Model):
    __tablename__ = "internships"

    internship_id = db.Column(db.Integer, primary_key=True)

    recruiter_id = db.Column(
        db.Integer,
        db.ForeignKey("recruiter_profiles.recruiter_id"),
        nullable=False
    )

    title = db.Column(db.String(150), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(150))
    work_mode = db.Column(db.String(30))
    duration = db.Column(db.String(50))
    stipend = db.Column(db.String(100))
    eligibility = db.Column(db.Text)
    required_skills = db.Column(db.Text)

    skills = db.relationship("Skill", secondary=internship_skills, backref="internships")

    deadline = db.Column(db.Date)
    status = db.Column(db.String(30), nullable=False, default="Open")

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )