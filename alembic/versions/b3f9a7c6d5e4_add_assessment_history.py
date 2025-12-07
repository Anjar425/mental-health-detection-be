"""add assessment_history table

Revision ID: b3f9a7c6d5e4
Revises: d6186824e10b
Create Date: 2025-12-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3f9a7c6d5e4'
down_revision: Union[str, Sequence[str], None] = 'd6186824e10b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'assessment_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('depression_score', sa.Integer(), nullable=True),
        sa.Column('anxiety_score', sa.Integer(), nullable=True),
        sa.Column('stress_score', sa.Integer(), nullable=True),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('highest_severity', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assessment_history_id'), 'assessment_history', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_assessment_history_id'), table_name='assessment_history')
    op.drop_table('assessment_history')
