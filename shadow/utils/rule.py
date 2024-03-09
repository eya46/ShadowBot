from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.rule import Rule

from shadow.utils.const import SUPERUSERS


def _OnlyMe(event: MessageEvent):
    return event.get_user_id() in SUPERUSERS


OnlyMe = Rule(_OnlyMe)
