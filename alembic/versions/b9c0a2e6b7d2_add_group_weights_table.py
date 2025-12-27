"""add group_weights table

Revision ID: b9c0a2e6b7d2
Revises: ac4b43b09239
Create Date: 2025-12-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b9c0a2e6b7d2'
down_revision: Union[str, Sequence[str], None] = 'ac4b43b09239'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'group_weights',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False, unique=True),
        sa.Column('weights', sa.Text(), nullable=True),
        sa.Column('signature', sa.String(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    )
    op.create_index(op.f('ix_group_weights_group_id'), 'group_weights', ['group_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_group_weights_group_id'), table_name='group_weights')
    op.drop_table('group_weights'
)
