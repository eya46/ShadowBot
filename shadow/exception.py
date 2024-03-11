from asyncio import iscoroutinefunction
from functools import wraps
from traceback import print_exc

from nonebot.exception import SkippedException, NoneBotException
from nonebot.utils import run_sync

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
                raise SkippedException()
            return ret
        except SkippedException:
            raise
        except Exception as e:
            if type(e) in [ActionError, NoneBotException]:
                raise e
            print_exc()
            raise ActionError(e) from e

    return _
