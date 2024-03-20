from typing import TypeVar

from nonebot import get_driver

SUPERUSERS = get_driver().config.superusers

assert len(SUPERUSERS) > 0

T = TypeVar("T")
OT = T | None
