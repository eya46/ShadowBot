from functools import partial, wraps

from httpx import AsyncClient
from nonebot.internal.params import Depends


async def _():
    pass


async def _httpx(*args, **kwargs):
    async with AsyncClient(*args, **kwargs) as client:
        yield client


def HTTPX(*args, **kwargs) -> AsyncClient:
    return Depends(wraps(_)(partial(_httpx, *args, **kwargs)))
