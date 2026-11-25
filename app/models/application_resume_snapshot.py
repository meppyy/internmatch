from datetime import datetime

from ..extensions import db


class ApplicationResumeSnapshot(db.Model):
    """
    Stores an independent, immutable resume document
    associated with a submitted internship application.
    """

    __tablename__ = "application_resume_snapshots"

    application_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "applications.application_id",
            ondelete="CASCADE"
        ),
        primary_key=True
    )

    file_name = db.Column(
        db.String(255),
        nullable=False
    )

    file_path = db.Column(
        db.String(500),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    application = db.relationship(
        "Application",
        back_populates="resume_snapshot"
    )