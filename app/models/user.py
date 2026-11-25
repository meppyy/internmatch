from datetime import datetime

from flask_login import UserMixin

from sqlalchemy import text, true
from ..extensions import db

class User(UserMixin, db.Model):
    __tablename__ = "users"

    student_profile = db.relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    recruiter_profile = db.relationship(
        "RecruiterProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        server_default=true()
    )

    session_version = db.Column(
        db.Integer,
        nullable=False,
        default=0,
        server_default=text("0")
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def get_id(self):
        return str(self.user_id)