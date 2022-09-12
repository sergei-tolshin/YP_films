import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.base import query_params
from core.config import messages
from models.film import FilmListResponse, FilmResponse
from services.film import ElasticCachedFilmService, get_film_service, get_min_permission_level

router = APIRouter(prefix="/film", tags=["film"])

film_query_params = query_params(["imdb_rating", "title.raw", "_score", "id"])

logger = logging.getLogger(__name__)


@router.get("/", response_model=list[FilmListResponse])
async def film_list(
        common_params: dict = Depends(film_query_params),
        filter_genre: str | None = Query(None),
        film_service: ElasticCachedFilmService = Depends(get_film_service),
) -> list[FilmListResponse]:
    """Function return all films in index, with sorting by value sort."""
    common_params["filter_genre"] = filter_genre
    try:
        films = await film_service.get_list(**common_params)
    except film_service.FilmBadRequestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    if not films:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.not_found.film.list
        )
    list_films = [FilmListResponse(**film.dict()) for film in films]
    return list_films


@router.get("/search", response_model=list[FilmListResponse])
async def film_search(
        query: str,
        common_params: dict = Depends(film_query_params),
        film_service: ElasticCachedFilmService = Depends(get_film_service),
) -> list[FilmListResponse]:
    """Function return films list by search query."""
    try:
        films = await film_service.get_search(query, **common_params)
    except film_service.FilmBadRequestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    if not films:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.not_found.film.list
        )
    list_films = [FilmListResponse(**film.dict()) for film in films]
    return list_films


# pylint: disable=redefined-builtin
@router.get("/{id}", response_model=FilmResponse)
async def film_details(
        id: UUID,
        film_service: ElasticCachedFilmService = Depends(get_film_service),
        #permission_level=Depends(get_min_permission_level) #why ?
) -> FilmResponse:
    """Function return film by id."""
    try:
        film = await film_service.get(id_=id)
    except film_service.FilmBadRequestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    if not film:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.not_found.film.item
        )
    #if film.min_access_level > permission_level["permission_level"]:
    #    raise HTTPException(
    #        status_code=status.HTTP_403_FORBIDDEN, detail=messages.forbidden.film.item
    #    )
    return FilmResponse(**film.dict())
