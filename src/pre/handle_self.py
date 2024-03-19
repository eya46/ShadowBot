from nonebot import on
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent, PrivateMessageEvent


@on("message_sent", block=True).handle()
async def _(event: Event, bot: Bot):
    n = event.copy()
    if n.message_type == "private":
        n.post_type = "message"
        n = PrivateMessageEvent.model_validate(n.model_dump())
        await bot.handle_event(n)
    elif n.message_type == "group":
        n.post_type = "message"
        n = GroupMessageEvent.model_validate(n.model_dump())
        await bot.handle_event(n)
