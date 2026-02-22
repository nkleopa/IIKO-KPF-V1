from fastapi import APIRouter

from app.api.v1.endpoints import branches, dashboard, dish_categories, labor, revenue, sync, waiter_checks, writeoffs

v1_router = APIRouter()

v1_router.include_router(dashboard.router)
v1_router.include_router(revenue.router)
v1_router.include_router(labor.router)
v1_router.include_router(writeoffs.router)
v1_router.include_router(sync.router)
v1_router.include_router(branches.router)
v1_router.include_router(waiter_checks.router)
v1_router.include_router(dish_categories.router)
