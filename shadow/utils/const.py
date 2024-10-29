from typing import TypeVar

from nonebot.permission import SuperUser
from nonebot.internal.rule import Rule

T = TypeVar("T")
OT = T | None


class Undefined:
    def __repr__(self):
        return "UNDEFINED"


SuperUserObj = SuperUser()
SuperUserRule = Rule(SuperUserObj)
