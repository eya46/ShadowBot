from nonebot import Bot
from nonebot.message import event_preprocessor
from nonebot.exception import IgnoredException
from nonebot.adapters.telegram import Bot as TelegramBot
from nonebot.adapters.onebot.v11 import Bot as V11Bot
from nonebot.internal.adapter.event import Event

from shadow.utils.const import SUPERUSERS


@event_preprocessor
def only_me_check(bot: Bot, event: Event):
    # V11Bot & self_id in SUPERUSERS 的消息
    if isinstance(bot, V11Bot) and bot.self_id in SUPERUSERS:
        return

    # TelegramBot & get_user_id in SUPERUSERS 的消息
    if isinstance(bot, TelegramBot) and event.get_user_id() in SUPERUSERS:
        return

    raise IgnoredException("not superuser")
