from nonebot import get_driver
from nonebot.rule import Rule
from nonebot.permission import SuperUser
from nonebot.internal.adapter import Event

StartCommands = tuple(get_driver().config.command_start)


def _UseStart(event: Event):
    if len(txt := event.get_plaintext()) == 0:
        return False
    return txt.startswith(StartCommands)


OnlyMe = Rule(SuperUser())

UseStart = Rule(_UseStart)
