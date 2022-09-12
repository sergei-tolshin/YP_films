import logging
from collections import OrderedDict

from fastapi import Query, exceptions, status
from core.config import DEFAULT_PAGE_SIZE

logger = logging.getLogger(__name__)


def _sort_choice(sort: str) -> tuple[str, str]:
    sort = sort.replace(".raw", "")
    if sort == "_score":
        sort = "relevance"
    asc, desc = sort, f"-{sort}"

    return asc, desc


def _generate_sort_map(sort_fields: list) -> OrderedDict:
    res = OrderedDict()
    for sort_field in sort_fields:
        asc, desc = _sort_choice(sort_field)
        res[desc] = sort_field
        res[asc] = sort_field
    return res


def query_params(sort_fields):
    gen_sort_map = _generate_sort_map(sort_fields)
    gen_sort_keys = list(gen_sort_map.keys())

    def wrapped(
        page: int | None = Query(1, alias="page[number]", ge=1),
        page_size: int
        | None = Query(DEFAULT_PAGE_SIZE, alias="page[size]", ge=1, le=1000),
        sort: str | None = Query(f"{gen_sort_keys[0]}", enum=gen_sort_keys),
    ):
        try:
            order = "desc" if sort and sort.startswith("-") else "asc"
            sort_field = gen_sort_map[sort]
        except (KeyError, IndexError) as exc:
            raise exceptions.HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"sort field must be one of: {', '.join(gen_sort_keys)}",
            ) from exc
        params = {
            "page": page,
            "page_size": page_size,
            "sort": sort_field,
            "order": order,
        }
        return params

    return wrapped
