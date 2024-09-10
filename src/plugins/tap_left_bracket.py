from nonebot import logger
from nonebot.message import event_preprocessor
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent

from src.provider.kv.utils import get_value


@event_preprocessor
async def _(bot: Bot, event: GroupMessageEvent):
    groups = await get_value("left_bracket_groups")
    if groups is None:
        return
    groups = groups.split(",")
    if str(event.group_id) not in groups:
        return

    message = event.message.extract_plain_text()
    if not message.endswith("（"):
        return

    try:
        await bot.call_api("set_msg_emoji_like", message_id=event.message_id, emoji_id="38")
    except Exception as e:
        logger.error(f"tap_left_bracket failed: {e}")
