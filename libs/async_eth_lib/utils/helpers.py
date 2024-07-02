import asyncio
import json
import os
import random
from typing import List

from aiohttp import (
    ClientSession
)

import libs.async_eth_lib.models.exceptions as exceptions


def join_path(path: str | tuple | list) -> str:
    if isinstance(path, str):
        return path
    return str(os.path.join(*path))


def read_txt(path: str | tuple | list) -> List[str]:
    path = join_path(path)
    with open(path, 'r') as file:
        return [row.strip() for row in file if row.strip()]


def read_json(
    path: str | tuple | list,
    encoding: str | None = None
) -> list | dict:
    path = join_path(path)
    return json.load(open(path, encoding=encoding))


def text_between(text: str, begin: str = '', end: str = '') -> str:
    """
    Extract a text between strings.

    :param str text: a source text
    :param str begin: a string from the end of which to start the extraction
    :param str end: a string at the beginning of which the extraction should end
    :return str: the extracted text or empty string if nothing is found
    """
    try:
        if not begin:
            start = 0
        else:
            start = text.index(begin) + len(begin)
    except:
        start = 0

    try:
        if end:
            end = text.index(end, start)
        else:
            end = len(text)
    except:
        end = len(text)

    extract = text[start:end]
    if extract == text:
        return ''

    return extract


async def sleep(sleep_from: int, sleep_to: int):
    random_value = random.randint(sleep_from, sleep_to)
    await asyncio.sleep(random_value)


async def make_request(
    method: str,
    url: str,
    headers: dict | None = None,
    **kwargs
) -> dict | None:
    async with ClientSession(headers=headers) as session:
        response = await session.request(method, url=url, **kwargs)

        status_code = response.status
        json_response = await response.json()

        if status_code <= 201:
            return json_response

        raise exceptions.HTTPException(
            response=json_response, status_code=status_code
        )
