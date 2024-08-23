from nonebot import Bot
from nonebot.message import event_preprocessor
from nonebot.exception import IgnoredException
from nonebot.adapters.onebot.v11 import Bot as V11Bot

from shadow.utils.const import SUPERUSERS


@event_preprocessor
def _(bot: Bot):
    # 只处理 V11Bot & SUPERUSERS 的消息
    if isinstance(bot, V11Bot) and bot.self_id in SUPERUSERS:
        return

    raise IgnoredException("not superuser")
