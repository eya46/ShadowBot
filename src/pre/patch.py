from typing import Set, Type, Tuple, Union, Optional, Dict, Any, Iterable

import nonebot
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, PrivateMessageEvent
from nonebot.dependencies import Dependent
from nonebot.internal.matcher import Matcher, current_event
from nonebot.internal.rule import Rule
from nonebot.rule import command
from nonebot.typing import T_RuleChecker, T_Handler

from shadow.exception import catch
from shadow.rule import OnlyMe
from shadow.utils.patch import impl


@impl(Matcher, classmethod)
def append_handler(
        cls: Matcher, handler: T_Handler, parameterless: Optional[Iterable[Any]] = None
) -> Dependent[Any]:
    handler = catch(handler)
    handler_ = Dependent[Any].parse(
        call=handler,
        parameterless=parameterless,
        allow_types=cls.HANDLER_PARAM_TYPES,
    )
    cls.handlers.append(handler_)
    return handler_


@impl(nonebot)
def on_command(
        cmd: Union[str, Tuple[str, ...]],
        rule: Optional[Union[Rule, T_RuleChecker]] = None,
        aliases: Optional[Set[Union[str, Tuple[str, ...]]]] = None,
        force_whitespace: Optional[Union[str, bool]] = None,
        _depth: int = 0,
        **kwargs,
) -> Type[Matcher]:
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
async def path_send(bot: Bot, api: str, data: Dict[str, Any]):
    if api not in ["send_msg", "send_private_msg"]:
        return
    event = current_event.get()
    if not isinstance(event, PrivateMessageEvent) or event.self_id != event.user_id:
        return
    data["user_id"] = getattr(event, "target_id", event.user_id)
