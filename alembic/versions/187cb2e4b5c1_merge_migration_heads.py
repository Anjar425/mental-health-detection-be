"""merge migration heads

Revision ID: 187cb2e4b5c1
Revises: assessment_history_add_group_fields, b9c0a2e6b7d2
Create Date: 2025-12-26 21:35:41.730746

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '187cb2e4b5c1'
down_revision: Union[str, Sequence[str], None] = ('assessment_history_add_group_fields', 'b9c0a2e6b7d2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
