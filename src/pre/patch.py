from typing import Any
from collections.abc import Iterable

import nonebot
from nonebot import on_message
from nonebot.rule import command
from arclet.alconna import config as alconna_config
from nonebot.typing import T_State, T_Handler, T_RuleChecker, T_PermissionChecker
from nonebot.permission import SUPERUSER
from nonebot.dependencies import Dependent
from nonebot.internal.rule import Rule
import nonebot_plugin_alconna
from nonebot.internal.params import Depends
from nonebot.internal.adapter import Event
from nonebot.internal.matcher import Matcher, current_event
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, PrivateMessageEvent
from nonebot.internal.permission import Permission

from shadow.rule import OnlyMe
from shadow.exception import catch
from shadow.utils.patch import patch

alconna_config.default_namespace.builtin_option_name["help"] = {"--help"}

_raw_on_alconna = nonebot_plugin_alconna.on_alconna


@patch(nonebot_plugin_alconna, name="on_alconna")
def patch_on_alconna(*args, **kwargs):
    if (permission := kwargs.get("permission")) is None:
        kwargs["permission"] = SUPERUSER
    else:
        permission: Permission | T_PermissionChecker
        kwargs["permission"] = permission | SUPERUSER
    return _raw_on_alconna(*args, **kwargs)


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


@patch(nonebot, name="on_command")
def patch_on_command(
    cmd: str | tuple[str, ...],
    rule: Rule | T_RuleChecker | None = None,
    aliases: set[str | tuple[str, ...]] | None = None,
    force_whitespace: str | bool | None = None,
    _depth: int = 0,
    **kwargs,
) -> type[Matcher]:
    """注册一个消息事件响应器，并且当消息以指定命令开头时响应。

    命令匹配规则参考: `命令形式匹配 <rule.md#command-command>`_

    参数:
        cmd: 指定命令内容
        rule: 事件响应规则
        aliases: 命令别名
        force_whitespace: 是否强制命令后必须有指定空白符
        permission: 事件响应权限
        handlers: 事件处理函数列表
        temp: 是否为临时事件响应器（仅执行一次）
        expire_time: 事件响应器最终有效时间点，过时即被删除
        priority: 事件响应器优先级
        block: 是否阻止事件向更低优先级传递
        state: 默认 state
    """

    commands = {cmd} | (aliases or set())
    kwargs.setdefault("block", False)
    rule = rule & OnlyMe if rule else OnlyMe
    return on_message(
        command(*commands, force_whitespace=force_whitespace) & rule,
        **kwargs,
        _depth=_depth + 1,  # type:ignore
    )


@Bot.on_calling_api
async def patch_send(bot: Bot, api: str, data: dict[str, Any]):
    if api not in ["send_msg", "send_private_msg"]:
        return
    event = current_event.get()
    if not isinstance(event, PrivateMessageEvent) or event.self_id != event.user_id:
        return
    data["user_id"] = getattr(event, "target_id", event.user_id)
