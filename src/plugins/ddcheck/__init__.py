# MIT
# https://github.com/noneplugin/nonebot-plugin-ddcheck

from http.cookies import SimpleCookie
from typing import Annotated

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot_plugin_alconna import UniMessage

from shadow.exception import ActionError
from shadow.utils.rule import OnlyMe
from shadow.utils.send import Tap
from .data_source import get_reply
from src.provider.kv.utils import GetValue

ddcheck = on_command("查成分", rule=OnlyMe)


@ddcheck.handle()
async def _(
        raw_cookie: Annotated[str, GetValue("bilibili_cookie")],
        msg: Message = CommandArg(),
):
    text = msg.extract_plain_text().strip()
    if not text:
        return
    cookie = SimpleCookie()
    cookie.load(raw_cookie)
    cookies = {key: value.value for key, value in cookie.items()}

    try:
        result = await get_reply(text, cookies)
    except Exception as e:
        logger.exception(e)
        return await Tap()

    if isinstance(result, str):
        raise ActionError(result)

    await UniMessage.image(raw=result).send()
