from nonebot import on
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent, PrivateMessageEvent


@on("message_sent", block=True, priority=0).handle()
async def _(event: Event, bot: Bot):
    n = event.model_dump()
    if n.get("message_type") == "private":
        n["post_type"] = "message"
        await bot.handle_event(PrivateMessageEvent.model_validate(n))
    elif n.get("message_type") == "group":
        n["post_type"] = "message"
        await bot.handle_event(GroupMessageEvent.model_validate(n))
