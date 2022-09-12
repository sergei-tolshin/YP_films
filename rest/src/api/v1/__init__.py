from fastapi import APIRouter

from api.v1.film import router as film_router
from api.v1.genre import router as genre_router
from api.v1.person import router as person_router

router = APIRouter(prefix="/v1")
router.include_router(film_router)
router.include_router(genre_router)
router.include_router(person_router)
