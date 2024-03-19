from httpx import AsyncClient
from nonebot.internal.params import Depends


async def _():
    pass


def HTTPX(*args, **kwargs) -> AsyncClient:
    async def _httpx():
        async with AsyncClient(*args, **kwargs) as client:
            yield client

    return Depends(_httpx)
