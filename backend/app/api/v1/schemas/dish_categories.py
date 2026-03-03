from pydantic import BaseModel, Field


class DishCategoryRow(BaseModel):
    id: int
    dish_group: str
    fullness_category: str | None
    parent_group: str | None
    fullness_weight: int


class DishCategoryUpdate(BaseModel):
    fullness_category: str | None = None  # "main" | "side" | "drink" | "dessert" | null
    fullness_weight: int | None = Field(default=None, ge=1, le=10)
