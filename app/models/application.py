from datetime import datetime

from ..extensions import db


class Application(db.Model):
    __tablename__ = "applications"

    application_id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student_profiles.student_id"),
        nullable=False
    )

    internship_id = db.Column(
        db.Integer,
        db.ForeignKey("internships.internship_id"),
        nullable=False
    )

    resume_id = db.Column(
        db.Integer,
        db.ForeignKey("resumes.resume_id"),
        nullable=False
    )

    application_date = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Applied"
    )

    match_score = db.Column(db.Float)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    student = db.relationship(
        "StudentProfile",
        back_populates="applications"
    )

    internship = db.relationship(
        "Internship",
        back_populates="applications"
    )

    resume = db.relationship(
        "Resume",
        back_populates="applications"
    )