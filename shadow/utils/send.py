from nonebot.adapters.onebot.v11 import MessageSegment

from nonebot.matcher import current_matcher, current_event


async def Tap():
    matcher = current_matcher.get()
    event = current_event.get()
    await matcher.send(MessageSegment("poke", {"qq": int(event.get_user_id())}))
