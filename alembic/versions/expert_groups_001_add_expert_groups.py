"""add expert_groups and association table

Revision ID: expert_groups_001
Revises: ac4b43b09239
Create Date: 2025-12-26

"""
from alembic import op
import sqlalchemy as sa

revision = 'expert_groups_001'
down_revision = 'ac4b43b09239'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'expert_groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'expert_group_association',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['group_id'], ['expert_groups.id']),
        sa.PrimaryKeyConstraint('user_id', 'group_id')
    )

def downgrade() -> None:
    op.drop_table('expert_group_association')
    op.drop_table('expert_groups')
