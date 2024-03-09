from typing import Optional, List

from nonebot.internal.matcher import Matcher
from nonebot.params import Depends
from nonebot_plugin_orm import get_session
from sqlalchemy import select, update

from .model import KV


def GetValue(key: str, fail_tip: Optional[str] = None) -> str:
    async def _(matcher: Matcher):
        if __ := await get_value(key):
            return __
        await matcher.finish(fail_tip or f"未设置{key}")

    return Depends(_)


def GetKV(key, fail_tip: Optional[str] = None) -> KV:
    async def _(matcher: Matcher):
        if __ := await get_kv(key):
            return __
        await matcher.finish(fail_tip or f"未设置{key}")

    return Depends(_)


async def add_kv(key: str, value: str) -> bool:
    """
    :param key: key
    :param value: value
    :return: True 新增， False 更新
    """
    async with get_session() as session:
        try:
            if await get_kv(key):
                await session.execute(update(KV).where(KV.key == key).values(value=value))
                return False
            else:
                session.add(KV(key=key, value=value))
                return True
        finally:
            await session.commit()


async def get_kv(key: str) -> Optional[KV]:
    async with get_session() as session:
        return await session.get(KV, str(key))


async def get_value(key: str) -> Optional[str]:
    async with get_session() as session:
        return kv.value if (kv := await session.get(KV, str(key))) else None


async def all_kv() -> List[KV]:
    async with get_session() as session:
        return list((await session.scalars(select(KV))).all())


async def del_kv(key: str, commit: bool = False) -> bool:
    async with get_session() as session:
        if kv := await get_kv(key):
            await session.delete(kv)
            if commit:
                await session.commit()
            return True
        else:
            return False
