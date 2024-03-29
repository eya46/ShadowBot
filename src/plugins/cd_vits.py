from urllib.parse import quote

from httpx import AsyncClient
from nonebot import get_driver, on_message
from nonebot.rule import Rule
from nonebot.params import T_State, EventPlainText
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageSegment

from shadow.req import HTTPX
from shadow.rule import OnlyMe, UseStart
from shadow.exception import ActionError

command_start = " ".join(get_driver().config.command_start)


async def split(state: T_State, text: str = EventPlainText()) -> bool:
    text = text.strip().strip(command_start)
    _ = text.split("说", 1)
    if len(_) != 2:
        return False
    state["role"] = _[0]
    state["text"] = _[1]
    return True


@on_message(block=False, priority=50, rule=OnlyMe & UseStart & Rule(split)).handle()
async def _(matcher: Matcher, state: T_State, client: AsyncClient = HTTPX()):
    role = state["role"]
    text = state["text"]

    resp = await client.get("https://www.xn--wxtz62e.site/models")
    models = {i.split(":", 1)[1]: i.split(":", 1)[0] for i in resp.json()["models"]}

    if models.get(role) is None:
        raise ActionError("没有该角色")

    await matcher.send(
        MessageSegment.record(
            f"https://www.xn--wxtz62e.site/run?length=1&noise=0.2&noisew=0.37&text={quote(text)}&id_speaker={models[role]}",
        )
    )
