"""add fullness columns to waiter_checks

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-22 12:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('waiter_checks', sa.Column('avg_fullness', sa.Numeric(precision=3, scale=1), nullable=True))
    op.add_column('waiter_checks', sa.Column('pct_ideal', sa.Numeric(precision=5, scale=1), nullable=True))


def downgrade() -> None:
    op.drop_column('waiter_checks', 'pct_ideal')
    op.drop_column('waiter_checks', 'avg_fullness')
