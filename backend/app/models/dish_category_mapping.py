from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin


class DishCategoryMapping(TimestampMixin, Base):
    __tablename__ = "dish_category_mappings"
    __table_args__ = (
        UniqueConstraint("dish_group", name="uq_dish_category_mapping_dish_group"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    dish_group: Mapped[str] = mapped_column(String(255))
    fullness_category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    parent_group: Mapped[str | None] = mapped_column(String(255), nullable=True)
