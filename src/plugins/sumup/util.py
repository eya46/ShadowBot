from typing import Literal

import dashscope
from nonebot.utils import run_sync
from nonebot_plugin_alconna import Reply, UniMsg

ai_caller = run_sync(dashscope.Generation.call)


async def check_msg_type(msg: UniMsg) -> tuple[Literal["text"], any]:
    reply = None
    if Reply in msg:
        reply = str(msg[Reply, 0].msg)

    return "text", (reply, str(msg.extract_plain_text())) if reply else (msg.extract_plain_text(), None)
