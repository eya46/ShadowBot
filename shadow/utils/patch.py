from types import FunctionType


def impl(obj, pre=None):
    def _patch(func: FunctionType):
        if pre:
            func = pre(func)
        setattr(obj, func.__name__, func)
        return func

    return _patch
