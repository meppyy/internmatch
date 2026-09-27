from datetime import datetime

from ..extensions import db


class RecruiterProfile(db.Model):
    __tablename__ = "recruiter_profiles"

    recruiter_id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        unique=True,
        nullable=False
    )

    company_name = db.Column(db.String(150), nullable=False)
    company_description = db.Column(db.Text)
    contact_phone = db.Column(db.String(20))

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )