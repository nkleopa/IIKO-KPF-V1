from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.v1.schemas.dish_categories import DishCategoryRow, DishCategoryUpdate
from app.dependencies import SessionDep
from app.models.dish_category_mapping import DishCategoryMapping

router = APIRouter(prefix="/dish-categories", tags=["dish-categories"])


@router.get("", response_model=list[DishCategoryRow])
async def list_dish_categories(session: SessionDep):
    result = await session.execute(
        select(DishCategoryMapping).order_by(DishCategoryMapping.dish_group)
    )
    return [
        DishCategoryRow(
            id=row.id,
            dish_group=row.dish_group,
            fullness_category=row.fullness_category,
            parent_group=row.parent_group,
        )
        for row in result.scalars().all()
    ]


@router.put("/{mapping_id}", response_model=DishCategoryRow)
async def update_dish_category(
    mapping_id: int,
    body: DishCategoryUpdate,
    session: SessionDep,
):
    result = await session.execute(
        select(DishCategoryMapping).where(DishCategoryMapping.id == mapping_id)
    )
    mapping = result.scalar_one_or_none()
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")

    mapping.fullness_category = body.fullness_category
    await session.commit()
    await session.refresh(mapping)
    return DishCategoryRow(
        id=mapping.id,
        dish_group=mapping.dish_group,
        fullness_category=mapping.fullness_category,
        parent_group=mapping.parent_group,
    )
