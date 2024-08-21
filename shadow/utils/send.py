from nonebot import get_driver
from nonebot.matcher import current_event, current_matcher
from nonebot.internal.matcher import current_bot
from nonebot.adapters.onebot.v11 import MessageSegment

use_poke: bool = getattr(get_driver().config, "use_poke", False)
use_emoji: bool = getattr(get_driver().config, "use_emoji", False)


async def DoSuccess(message_id: str | None = None):
    matcher = current_matcher.get()
    event = current_event.get()
    bot = current_bot.get()
    if message_id is None:
        message_id = matcher.state.get("_message_id")
    if use_poke:
        return await matcher.send(MessageSegment("poke", {"qq": int(event.get_user_id())}))
    elif use_emoji and message_id:
        return await bot.call_api("set_msg_emoji_like", message_id=message_id, emoji_id="124")

    raise Exception("DoSuccess failed")


async def DoFail(message_id: str | None = None):
    matcher = current_matcher.get()
    event = current_event.get()
    bot = current_bot.get()
    if message_id is None:
        message_id = matcher.state.get("_message_id")

    if use_poke:
        await matcher.send(MessageSegment("poke", {"qq": int(event.get_user_id())}))
        await matcher.send(MessageSegment("poke", {"qq": int(event.get_user_id())}))
        return
    elif use_emoji and message_id:
        return await bot.call_api("set_msg_emoji_like", message_id=message_id, emoji_id="38")

    raise Exception("DoFail failed")
