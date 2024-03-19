from functools import partial

from nonebot.matcher import current_matcher
from nonebot.internal.params import Depends

from shadow.utils.const import OT


def get_arg(key, default: OT = None):
    _m = current_matcher.get()
    return _m.get_arg(key) or default


def set_arg(key, value):
    current_matcher.get().set_arg(key, value)


def GetArg(key, default: OT = None):
    return Depends(partial(get_arg, key, default))
