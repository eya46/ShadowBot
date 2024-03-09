from nonebot import require
from nonebot.exception import ActionFailed
from nonebot.message import run_postprocessor
from nonebot_plugin_alconna import UniMessage, Target
from nonebot_plugin_alconna.uniseg import Receipt

from shadow.exception import ActionError
from shadow.utils.send import Tap

require("kv")

from src.provider.kv.utils import get_value


async def send_error(msg: str | UniMessage) -> Receipt:
    if not isinstance(msg, UniMessage):
        msg = UniMessage(msg)
    group_id = await get_value("error_group")
    assert group_id is not None
    return await msg.send(target=Target(id=group_id))


@run_postprocessor
async def _catch1(error: ActionError | ActionFailed):
    if isinstance(error, ActionError):
        try:
            await UniMessage(error.msg).send(target=Target(id=await get_value("error_group")))
        except:
            await Tap()
            await Tap()
    else:
        await Tap()
        await Tap()
