from collections.abc import Sequence

from sqlalchemy import Executable
from arclet.alconna import Arparma
from nonebot_plugin_orm import async_scoped_session
from nonebot_plugin_alconna import UniMsg, AlconnaMatches
from nonebot.internal.params import Depends


def assert_dep(path: str, sql: Executable):
    async def _dep(sess: async_scoped_session, args: Arparma = AlconnaMatches()):
        if args.find(f"~{path}"):
            return await sess.execute(sql)
        return None

    return Depends(_dep)


def if_ok(msg: UniMsg | str, txt: Sequence[str] | None = None):
    if txt is None:
        txt = ["好", "是", "行", "yes", "y", "ok"]
    if isinstance(msg, UniMsg):
        msg = msg.extract_plain_text()
    for i in txt:
        if i == msg:
            return True
    return False


def OK(txt: Sequence[str] | None = None):
    if txt is None:
        txt = ["好", "是", "行", "yes", "y", "ok"]

    def _if_ok(msg: UniMsg | str):
        if isinstance(msg, UniMsg):
            msg = msg.extract_plain_text()
        for i in txt:
            if i == msg:
                return True
        return False

    return Depends(_if_ok)
