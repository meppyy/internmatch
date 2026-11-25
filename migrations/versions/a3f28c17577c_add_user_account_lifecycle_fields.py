"""Add user account lifecycle fields."""

from alembic import op
import sqlalchemy as sa


revision = "a3f28c17577c"
down_revision = "d7e8f9a0b1c2"
branch_labels = None
depends_on = None


def _has_resume_student_unique_constraint():
    """Check whether resumes.student_id is already unique."""

    inspector = sa.inspect(op.get_bind())

    constraints = inspector.get_unique_constraints("resumes")
    indexes = inspector.get_indexes("resumes")

    for constraint in constraints:
        if set(constraint.get("column_names") or []) == {"student_id"}:
            return True

    for index in indexes:
        if (
            index.get("unique")
            and set(index.get("column_names") or []) == {"student_id"}
        ):
            return True

    return False


def upgrade():
    # Repair the original schema only when its unique constraint
    # is missing. Production may already have this constraint.
    if not _has_resume_student_unique_constraint():
        with op.batch_alter_table("resumes") as batch_op:
            batch_op.create_unique_constraint(
                "uq_resumes_student_id",
                ["student_id"]
            )

    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_active",
                sa.Boolean(),
                server_default=sa.true(),
                nullable=False
            )
        )

        batch_op.add_column(
            sa.Column(
                "session_version",
                sa.Integer(),
                server_default=sa.text("0"),
                nullable=False
            )
        )


def downgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("session_version")
        batch_op.drop_column("is_active")

    # Retain resumes.student_id uniqueness. It belongs to the
    # original schema and may have existed before this revision.