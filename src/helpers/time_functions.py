import time
import asyncio
import random
from datetime import datetime

from src._types.common import IntRange


def get_izoformat_timestamp() -> str:
    """
    Get the current timestamp.

    Returns:
        str: the current timestamp.

    """
    return datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'


def get_unix_timestamp() -> str:
    return str(int(time.time() * 1000))


async def sleep(value: int | IntRange):
    if isinstance(value, int):
        await asyncio.sleep(value)
    else:
        random_value = random.randint(value[0], value[1])
        await asyncio.sleep(random_value)
