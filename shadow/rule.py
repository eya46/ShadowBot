from nonebot import get_driver
from nonebot.rule import Rule
from nonebot.permission import SuperUser
from nonebot.internal.adapter import Event

from shadow.utils.const import SUPERUSERS


def _OnlyMe(event: Event):
    return event.get_user_id() in SUPERUSERS


_start = tuple(get_driver().config.command_start)


def _UseStart(event: Event):
    if len(txt := event.get_plaintext()) == 0:
        return False
    return txt.startswith(_start)


OnlyMe = Rule(SuperUser())

UseStart = Rule(_UseStart)
