import asyncio
import json
import os
import random
from typing import Any, List

from aiohttp import (
    ClientSession
)

from ..models import exceptions as exceptions


def center_output(message: str):
    print(f"| {message:^59}|")


def format_input(message: str) -> str:
    print(f"| {message:^59}|", end='\n| ', flush=True)
    value = input()

    return value


def count_lines(file_path: str) -> int:
    with open(file_path, 'r', encoding='utf-8') as file:
        return sum(1 for _ in file)


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


def write_json(
    path: str | list[str],
    data: Any,
    indent: int = 4,
) -> None:
    if isinstance(path, list):
        path = join_path(path)
    with open(path, 'w') as file:
        json.dump(data, file, indent=indent)



def to_cut_hex_prefix_and_zfill(hex_data: str, length: int = 64):
    """
    Convert the hex string to lowercase, remove the '0x' prefix, and fill it with zeros to the specified length.

    Args:
        hex_data (str): The original hex string.
        length (int): The desired length of the string after filling. The default is 64.

    Returns:
        str: The modified string with '0x' prefix removed and zero-filled to the specified length.
    """
    if hex_data.startswith('0x'):
        hex_data = hex_data[2:]
    else:
        raise ValueError("Hex address must start with '0x'")

    return hex_data.zfill(length)


def normalize_non_evm_hex_value(hex_value: str, length: int = 64) -> str:
    hex_value = to_cut_hex_prefix_and_zfill(hex_value, length)
    return '0x' + hex_value


def text_between(text: str, begin: str = '', end: str = '') -> str:
    """
    Extract a text between strings.

    :param str text: a source text
    :param str begin: a string from the end of which to start the extraction
    :param str end: a string at the beginning of which the extraction should end
    :return str: the extracted text or empty string if nothing is found
    """
    end_value = 0
    
    try:
        if begin: start = text.index(begin) + len(begin)
        else: start = 0
    except:
        start = 0

    try:
        if end: end_value = text.index(end, start)
        else: end_value = -1
    except:
        end_value = -1

    extract = text[start:end_value]
    if extract == text:
        return ''

    return extract


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
