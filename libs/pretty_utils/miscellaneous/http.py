from typing import Any

from curl_cffi.requests import AsyncSession

import libs.pretty_utils.exceptions as exceptions

def normalize_http_params(
    params: dict[str, Any] | None
) -> dict[str, str | int | float] | None:
    if not params:
        return

    new_params = params.copy()
    for key, value in params.items():
        if not value:
            del new_params[key]

        if isinstance(value, bool):
            new_params[key] = str(value).lower()
        elif isinstance(value, bytes):
            new_params[key] = value.decode('utf-8')

    return new_params

async def make_async_request(
    method: str = 'GET',
    url: str = '',
    headers: dict | None = None,
    **kwargs
) -> dict | None:
    async with AsyncSession(headers=headers) as session:
        response = await session.request(method, url=url, **kwargs)

        status_code = response.status_code
        json_response = response.json()

        if status_code <= 201:
            return json_response

        raise exceptions.HTTPException(
            response=json_response, status_code=status_code
        )