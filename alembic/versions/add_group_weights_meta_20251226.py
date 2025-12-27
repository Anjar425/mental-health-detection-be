"""add group_weights meta and created_at

Revision ID: add_group_weights_meta_20251226
Revises: b9c0a2e6b7d2
Create Date: 2025-12-26 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = 'add_group_weights_meta_20251226'
down_revision = 'b9c0a2e6b7d2'
branch_labels = None
depends_on = None


def upgrade():
    # Add meta and created_at columns to group_weights if missing (created_at nullable, set existing rows to CURRENT_TIMESTAMP)
    conn = op.get_bind()
    cols = [r[1] for r in conn.execute(sa.text("PRAGMA table_info('group_weights')")).fetchall()]
    if 'meta' not in cols:
        op.add_column('group_weights', sa.Column('meta', sa.Text(), nullable=True))
    if 'created_at' not in cols:
        op.add_column('group_weights', sa.Column('created_at', sa.DateTime(), nullable=True))
        # Populate existing rows with current timestamp
        conn.execute(sa.text("UPDATE group_weights SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))


def downgrade():
    op.drop_column('group_weights', 'created_at')
    op.drop_column('group_weights', 'meta')
