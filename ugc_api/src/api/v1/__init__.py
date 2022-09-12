from fastapi import APIRouter

from api.v1.bookmark import router as bookmark_router
from api.v1.like import router as like_router
from api.v1.review import router as review_router
from api.v1.view import router as view_router

router = APIRouter(prefix="/v1")
router.include_router(bookmark_router)
router.include_router(like_router)
router.include_router(review_router)
router.include_router(view_router)
