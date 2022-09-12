from http import HTTPStatus

import pytest

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_api_schema(make_get_request, schema):
    response = await make_get_request("/openapi.json", root=True)
    openapi_schema = response.body

    assert response.status == HTTPStatus.OK
    assert openapi_schema == schema
