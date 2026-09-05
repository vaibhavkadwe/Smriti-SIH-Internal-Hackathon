"""P7 — weekly_reports table for persisted weekly clinical summaries.

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "weekly_reports",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", UUID(as_uuid=True),
                  sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("week_start", sa.DateTime(), nullable=False),
        sa.Column("generated_at", sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("report_json", sa.JSON(), nullable=False),
    )
    op.create_index("ix_weekly_reports_patient_id", "weekly_reports", ["patient_id"])
    op.create_index("ix_weekly_reports_week_start", "weekly_reports", ["week_start"])
    op.create_unique_constraint(
        "uq_weekly_reports_patient_week", "weekly_reports", ["patient_id", "week_start"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_weekly_reports_patient_week", "weekly_reports", type_="unique")
    op.drop_index("ix_weekly_reports_week_start", table_name="weekly_reports")
    op.drop_index("ix_weekly_reports_patient_id", table_name="weekly_reports")
    op.drop_table("weekly_reports")
