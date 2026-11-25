from datetime import datetime

from ..extensions import db


class ModerationAction(db.Model):
    __tablename__ = "moderation_actions"

    __table_args__ = (
        db.CheckConstraint(
            """
            (
                target_user_id IS NOT NULL
                AND target_internship_id IS NULL
            )
            OR
            (
                target_user_id IS NULL
                AND target_internship_id IS NOT NULL
            )
            """,
            name="ck_moderation_actions_exactly_one_target"
        ),
    )

    action_id = db.Column(
        db.Integer,
        primary_key=True
    )

    admin_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True
    )

    # Preserve administrator identity if that account is deleted.
    admin_name = db.Column(
        db.String(100),
        nullable=False
    )

    admin_email = db.Column(
        db.String(120),
        nullable=False
    )

    action_type = db.Column(
        db.String(50),
        nullable=False
    )

    # These are historical identifiers, deliberately not foreign keys.
    # Deleting the original record must not delete its audit history.
    target_user_id = db.Column(
        db.Integer,
        nullable=True
    )

    target_internship_id = db.Column(
        db.Integer,
        nullable=True
    )

    # Safe identifying snapshot; never store passwords or resume contents.
    target_snapshot = db.Column(
        db.Text,
        nullable=False
    )

    old_value = db.Column(
        db.Text,
        nullable=True
    )

    new_value = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )