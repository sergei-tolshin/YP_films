from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from core.config import messages
from models.genre import GenreResponse
from services.genre import get_genre_service, ElasticCachedGenreService

router = APIRouter(prefix="/genre", tags=["genre"])


@router.get("/", response_model=list[GenreResponse])
async def genre_list(
    service: ElasticCachedGenreService = Depends(get_genre_service),
) -> list[GenreResponse]:
    """Function return all genres in index, with sorting by value sort."""
    try:
        genres = await service.get_list(page_size=100, page=1)
    except service.GenreBadRequestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    if not genres:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.not_found.genre.list
        )
    list_genres = [GenreResponse(**obj.dict()) for obj in genres]
    return list_genres


# pylint: disable=redefined-builtin
@router.get("/{id}", response_model=GenreResponse)
async def genre_id(
    id: UUID, service: ElasticCachedGenreService = Depends(get_genre_service)
) -> GenreResponse:
    """Function return genre by id."""
    try:
        genre = await service.get(id)
    except service.GenreBadRequestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.not_found.genre.item
        )
    return GenreResponse(**genre.dict())
