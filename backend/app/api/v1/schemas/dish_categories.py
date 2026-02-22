from pydantic import BaseModel


class DishCategoryRow(BaseModel):
    id: int
    dish_group: str
    fullness_category: str | None
    parent_group: str | None


class DishCategoryUpdate(BaseModel):
    fullness_category: str | None  # "main" | "side" | "drink" | "dessert" | null
