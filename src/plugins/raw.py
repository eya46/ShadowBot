from json import dumps

from nonebot import on_command
from nonebot.internal.matcher import Matcher
from nonebot.adapters.onebot.v11.event import MessageEvent


@on_command("raw").handle()
async def _(matcher: Matcher, event: MessageEvent):
    reply = event.reply
    if reply is None:
        return

    await matcher.send(
        "\n------\n".join([f"{seg.type}:\n{dumps(seg.data, ensure_ascii=False)}" for seg in reply.message])
    )
