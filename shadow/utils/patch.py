from types import FunctionType
from typing import Callable


def patch(obj, pre: Callable | None = None, name: str | None = None):
    def _patch(func: FunctionType):
        if pre:
            func = pre(func)
        setattr(obj, name if name else func.__name__, func)
        return func

    return _patch
