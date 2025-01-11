import asyncio
import random


async def sleep(value: int | tuple[int, int]):
    if isinstance(value, int):
        await asyncio.sleep(value)
    else:
        random_value = random.randint(value[0], value[1])
        await asyncio.sleep(random_value)