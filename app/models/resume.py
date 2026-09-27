from datetime import datetime

from ..extensions import db


class Resume(db.Model):
    __tablename__ = "resumes"

    resume_id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student_profiles.student_id"),
        nullable=False
    )

    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    extracted_text = db.Column(db.Text)

    student = db.relationship(
        "StudentProfile",
        back_populates="resume"
    )

    applications = db.relationship(
        "Application",
        back_populates="resume"
    )

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )   