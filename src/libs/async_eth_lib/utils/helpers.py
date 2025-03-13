import json
import os
from typing import Any, List

from curl_cffi.requests import AsyncSession

from src._types.common import HttpMethod
from ..models import exceptions as exceptions


def join_path(path: list[str]) -> str:
    return str(os.path.join(*path))


def read_txt(path: str | list[str]) -> List[str]:
    if isinstance(path, list):
        path = join_path(path)
    with open(path, 'r') as file:
        return [row.strip() for row in file if row.strip()]


def read_json(
    path: str | list[str],
    encoding: str | None = None
) -> list[dict] | dict:
    if isinstance(path, list):
        path = join_path(path)
    return json.load(open(path, encoding=encoding))


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
    method: HttpMethod = 'GET',
    url: str = '',
    headers: dict | None = None,
    **kwargs
) -> dict:
    async with AsyncSession(headers=headers, trust_env=True) as session:
        response = await session.request(method, url=url, **kwargs)
        status_code = response.status_code
        json_response = response.json()

        if status_code <= 201:
            return json_response

        raise exceptions.HTTPException(
            response=json_response, status_code=status_code
        )
