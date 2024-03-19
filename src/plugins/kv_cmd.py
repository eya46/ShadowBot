from io import StringIO

from nonebot import logger, get_driver, on_command
from nonebot.utils import run_sync
from nonebot.params import CommandArg
from nonebot.internal.adapter import Message

from src.provider.kv.utils import get_value

cmd_start = list(get_driver().config.command_start)


def _print(*args, **kwargs):
    _ = StringIO()
    print(*args, **kwargs, file=_)
    logger.info(_.getvalue().strip())


@on_command(cmd_start[0], aliases=set(cmd_start[1:])).handle()
async def _(arg: Message = CommandArg()):
    arg = arg.extract_plain_text()
    if (code := await get_value(f"code_{arg}")) is None:
        return
    await run_sync(exec)(code, {"print": _print})
    return True
