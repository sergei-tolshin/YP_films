from api.v1.admin import router as admin_router
from fastapi import APIRouter

router = APIRouter(prefix="/v1")

router.include_router(admin_router)
