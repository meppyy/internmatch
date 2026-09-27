from datetime import datetime

from ..extensions import db


class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    student_id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        unique=True,
        nullable=False
    )

    phone = db.Column(db.String(20))
    education = db.Column(db.Text)
    profile_summary = db.Column(db.Text)
    experience = db.Column(db.Text)
    projects = db.Column(db.Text)
    certifications = db.Column(db.Text)

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )