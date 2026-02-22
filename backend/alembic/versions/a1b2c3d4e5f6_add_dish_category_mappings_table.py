"""add dish_category_mappings table

Revision ID: a1b2c3d4e5f6
Revises: f9e0c425fc3e
Create Date: 2026-02-22 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f9e0c425fc3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Default mappings from the plan
DEFAULT_MAPPINGS = [
    ("Хинкали", "main"),
    ("Мучное", "main"),
    ("Горячие блюда", "main"),
    ("Супы", "main"),
    ("Фестиваль Тако", "main"),
    ("Закуски и салаты", "side"),
    ("Допы", "side"),
    ("Соусы", "side"),
    ("Холодные напитки", "drink"),
    ("Кофе и чай", "drink"),
    ("Пиво", "drink"),
    ("Мин. вода", "drink"),
    ("Доп Чай", "drink"),
    ("Чай в чайнике", "drink"),
    ("Сладкое", "dessert"),
    ("Сахар", None),
    ("Упаковка", None),
    ("Подарок от шефа", None),
    ("БЛЮДА", None),
    ("ТОВАРЫ", None),
    ("Для Доставки", None),
    ("Дюжина Хинкали", None),
    ("Мама хинкали", None),
    ("Тако", None),
]


def upgrade() -> None:
    table = op.create_table(
        'dish_category_mappings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dish_group', sa.String(length=255), nullable=False),
        sa.Column('fullness_category', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('dish_group', name='uq_dish_category_mapping_dish_group'),
    )

    op.bulk_insert(
        table,
        [
            {"dish_group": dg, "fullness_category": cat}
            for dg, cat in DEFAULT_MAPPINGS
        ],
    )


def downgrade() -> None:
    op.drop_table('dish_category_mappings')
