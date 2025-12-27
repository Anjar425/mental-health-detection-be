"""merge add_group_weights_meta into main heads

Revision ID: merge_add_group_weights_meta_20251226
Revises: 187cb2e4b5c1, add_group_weights_meta_20251226
Create Date: 2025-12-26 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'merge_add_group_weights_meta_20251226'
down_revision = ('187cb2e4b5c1', 'add_group_weights_meta_20251226')
branch_labels = None
depends_on = None


def upgrade():
    # This is a merge-only revision. No DB operations.
    pass


def downgrade():
    pass
