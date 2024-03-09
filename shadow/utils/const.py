from typing import TypeVar

from nonebot import get_driver

SUPERUSERS = get_driver().config.superusers

T = TypeVar("T")
OT = T | None
