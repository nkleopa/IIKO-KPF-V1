"""repopulate dish_category_mappings for DishGroup.Parent hierarchy

The fullness calculation now groups at DishGroup.Parent level (subcategory)
instead of DishGroup.SecondParent (category). Existing rows are at the wrong
granularity — clear them so they repopulate correctly on the next waiter-check sync.

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-03-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DELETE FROM dish_category_mappings")


def downgrade() -> None:
    # Data cannot be restored; a re-sync is required either way.
    pass
