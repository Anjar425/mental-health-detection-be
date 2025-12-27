"""add group metadata to assessment history

Revision ID: assessment_history_add_group_fields
Revises: expert_groups_001
Create Date: 2025-12-26

"""
from alembic import op
import sqlalchemy as sa


revision = "assessment_history_add_group_fields"
down_revision = "expert_groups_001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("assessment_history", sa.Column("group_id", sa.Integer(), nullable=True))
    op.add_column("assessment_history", sa.Column("group_name", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("assessment_history", "group_name")
    op.drop_column("assessment_history", "group_id")
