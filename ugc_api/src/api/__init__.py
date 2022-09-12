from fastapi import APIRouter

from api.v1 import router as v1_router

router = APIRouter(prefix="/ugc/api")
router.include_router(v1_router)