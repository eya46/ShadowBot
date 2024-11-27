from typing import Any
from collections.abc import Iterable

from nonebot import logger
from arclet.alconna import config as alconna_config
from nonebot.typing import T_State, T_Handler
from nonebot.dependencies import Dependent
import nonebot_plugin_alconna
from nonebot.internal.params import Depends
from nonebot.internal.adapter import Event
from nonebot.internal.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageEvent

from shadow.exception import catch
from shadow.utils.patch import patch

alconna_config.default_namespace.builtin_option_name["help"] = {"--help"}

_raw_on_alconna = nonebot_plugin_alconna.on_alconna


@patch(nonebot_plugin_alconna.command_manager, name="load_cache")
@patch(nonebot_plugin_alconna.command_manager, name="dump_cache")
def command_manager_patch(*args, **kwargs):
    logger.info("nonebot_plugin_alconna.command_manager.load_cache/dump_cache is disabled")


async def set_message_id(event: Event, state: T_State):
    if isinstance(event, MessageEvent):
        state["_message_id"] = event.message_id


@patch(Matcher, classmethod)
def append_handler(cls: Matcher, handler: T_Handler, parameterless: Iterable[Any] | None = None) -> Dependent[Any]:
    handler = catch(handler)
    handler_ = Dependent[Any].parse(
        call=handler,
        parameterless=[Depends(set_message_id), *parameterless] if parameterless else [Depends(set_message_id)],
        allow_types=cls.HANDLER_PARAM_TYPES,
    )
    cls.handlers.append(handler_)
    return handler_
