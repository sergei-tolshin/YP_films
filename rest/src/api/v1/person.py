import elasticsearch.exceptions
from fastapi import APIRouter, Depends, HTTPException, status

from core.config import messages
from models.film import FilmListResponse
from models.person import PersonResponse
from services.person import (
    ElasticCachedPersonService,
    get_person_service,
)
from services.film import ElasticCachedFilmService, get_film_service
from api.base import query_params

router = APIRouter(prefix="/person", tags=["person"])


person_query_params = query_params(["full_name.raw", "_score"])


@router.get("/search", response_model=list[PersonResponse])
async def person_search(
    query: str,
    common_params: dict = Depends(person_query_params),
    service: ElasticCachedPersonService = Depends(get_person_service),
) -> list[PersonResponse]:
    """Function return Person list by search query."""
    params = common_params
    try:
        persons = await service.get_search(query, **params)
    except ElasticCachedPersonService.PersonBadRequestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    if not persons:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.not_found.person.list
        )
    person_responses = [
        PersonResponse(
            uuid=person.id,
            full_name=person.full_name,
            role=",".join([role.role for role in person.roles]) if person.roles else "",
            film_ids=sum((ids.film_work_ids for ids in person.roles), []) if person.roles else []
        )
        for person in persons
    ]
    return person_responses


# pylint: disable=redefined-builtin
@router.get("/{id}", response_model=PersonResponse)
async def person_id(
    id: str, service: ElasticCachedPersonService = Depends(get_person_service)
) -> PersonResponse:
    """Function return person by id."""
    try:
        person = await service.get(id)
    except ElasticCachedPersonService.PersonBadRequestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.not_found.person.item
        )
    return PersonResponse(
        uuid=person.id,
        full_name=person.full_name,
        role=",".join([role.role for role in person.roles]),
        film_ids=sum((ids.film_work_ids for ids in person.roles), []) if person.roles else [],
    )


@router.get("/{id}/film", response_model=list[FilmListResponse])
async def person_films(
    id: str, service: ElasticCachedFilmService = Depends(get_film_service)
) -> list[FilmListResponse]:
    """Function return film by person_id."""
    try:
        films = await service.get_films_by_person(id)
    except elasticsearch.exceptions.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    if not films:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.not_found.film.list
        )
    films_list = [FilmListResponse(**obj.dict()) for obj in films]
    return films_list
