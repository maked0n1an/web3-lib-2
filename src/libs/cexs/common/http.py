from curl_cffi.requests import AsyncSession

from ..common import exceptions as exc


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

        raise exc.HTTPException(
            response=json_response, status_code=status_code
        )
