from typing import Any

from httpx import AsyncClient
from nonebot import require
from nonebot.message import run_postprocessor
from nonebot.exception import ActionFailed, NoneBotException
from nonebot_plugin_alconna import Target, UniMessage
from nonebot_plugin_alconna.uniseg import Receipt

from shadow.exception import ActionError
from shadow.utils.send import DoFail

require("kv")

from src.provider.kv.utils import get_value


async def send_to_feishu(msg: Any | UniMessage):
    if isinstance(msg, UniMessage):
        msg = msg.extract_plain_text()

    async with AsyncClient() as client:
        await client.post(await get_value("error_api_feishu"), json={"msg_type": "text", "content": {"text": str(msg)}})


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
        except NoneBotException:
            await send_to_feishu(error.msg)
    else:
        await DoFail()

