from traceback import print_exc
from asyncio import iscoroutinefunction
from functools import wraps

from nonebot.utils import run_sync
from nonebot.exception import ActionFailed

from shadow.utils.send import Tap


class ActionError(Exception):
    def __init__(self, msg: str | Exception):
        self.msg = msg if isinstance(msg, str) else str(msg)


def catch(func):
    func = func if iscoroutinefunction(func) else run_sync(func)

    @wraps(func)
    async def _(*args, **kwargs):
        try:
            ret = await func(*args, **kwargs)
            if ret:
                await Tap()
            return ret
        except Exception as e:
            if type(e) in [ActionError, ActionFailed]:
                raise e
            print_exc()
            raise ActionError(e)

    return _
