from fastapi import APIRouter

from app.api.v1.endpoints import branches, dashboard, labor, revenue, sync, writeoffs

v1_router = APIRouter()

v1_router.include_router(dashboard.router)
v1_router.include_router(revenue.router)
v1_router.include_router(labor.router)
v1_router.include_router(writeoffs.router)
v1_router.include_router(sync.router)
v1_router.include_router(branches.router)
