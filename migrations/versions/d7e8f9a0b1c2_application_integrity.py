"""Allow optional resumes and prevent duplicate applications."""

from alembic import op
import sqlalchemy as sa


revision = "d7e8f9a0b1c2"
down_revision = "584d29daaad3"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("applications") as batch_op:
        batch_op.alter_column(
            "resume_id",
            existing_type=sa.Integer(),
            nullable=True
        )

        batch_op.create_unique_constraint(
            "uq_application_student_internship",
            ["student_id", "internship_id"]
        )


def downgrade():
    with op.batch_alter_table("applications") as batch_op:
        batch_op.drop_constraint(
            "uq_application_student_internship",
            type_="unique"
        )

        batch_op.alter_column(
            "resume_id",
            existing_type=sa.Integer(),
            nullable=False
        )