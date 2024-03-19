from nonebot import get_driver
from nonebot.rule import Rule
from nonebot.permission import SuperUser
from nonebot.adapters.onebot.v11 import MessageEvent

from shadow.utils.const import SUPERUSERS


def _OnlyMe(event: MessageEvent):
    return event.get_user_id() in SUPERUSERS


_start = tuple(get_driver().config.command_start)


def _UseStart(event: MessageEvent):
    if len(txt := event.get_plaintext()) == 0:
        return False
    return txt.startswith(_start)


OnlyMe = Rule(SuperUser())

UseStart = Rule(_UseStart)
