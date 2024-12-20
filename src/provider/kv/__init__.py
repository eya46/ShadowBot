from nonebot import logger
from arclet.alconna import Arg, Args, Alconna, Subcommand
from nonebot.permission import SUPERUSER
from nonebot_plugin_alconna import Check, Match, AlconnaMatch, assign, on_alconna

from shadow.utils.send import DoSuccess

from .utils import add_kv, all_kv, del_kv, get_kv

_kv = on_alconna(
    Alconna(
        "kv",
        Subcommand("set", Args["name", str], Arg("value", str, seps="\n")),
        Subcommand("update", Args["name", str], Arg("value", str, seps="\n")),
        Subcommand("get", Arg("name", str)),
        Subcommand("del", Arg("name", str)),
        Subcommand("all"),
    ),
    permission=SUPERUSER,
)


@_kv.handle(parameterless=[Check(assign("set"))])
@_kv.handle(parameterless=[Check(assign("update"))])
async def _set_or_update(name: Match[str] = AlconnaMatch("name"), value: Match[str] = AlconnaMatch("value")):
    logger.success(f"{'添加' if (await add_kv(name.result, value.result)) else '更新'} {name.result} 成功")
    await DoSuccess()


@_kv.assign("get")
async def _get(name: Match[str] = AlconnaMatch("name")):
    if kv := await get_kv(name.result):
        await _kv.finish(f"key:\n{name.result}\nvalue:\n{kv.value}")
    else:
        await _kv.finish(f"key:{name.result},未设置")


@_kv.assign("del")
async def _del(name: Match[str] = AlconnaMatch("name")):
    logger.success(f"key:\n{name.result}\n删除 {'成功' if await del_kv(name.result, commit=True) else '失败'}")
    await DoSuccess()


@_kv.assign("all")
async def _all():
    kvs = await all_kv()
    await _kv.finish("kv:\n" + "\n".join([kv.key for kv in kvs]))


__all__ = []
