from nonebot import on
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent, PrivateMessageEvent


@on("message_sent", block=True).handle()
async def _(event: Event, bot: Bot):
    n = event.model_dump()
    if n.get("message_type") == "private":
        n.post_type = "message"
        n = PrivateMessageEvent.model_validate(n)
        await bot.handle_event(n)
    elif n.get("message_type") == "group":
        n.post_type = "message"
        n = GroupMessageEvent.model_validate(n)
        await bot.handle_event(n)
