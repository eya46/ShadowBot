# MeetWq
# MIT
# https://github.com/noneplugin/nonebot-plugin-emojimix

import re

import emoji
from nonebot import on_message, get_driver
from nonebot.params import EventPlainText
from nonebot.rule import Rule
from nonebot.typing import T_State
from nonebot_plugin_alconna import UniMessage

from shadow.rule import OnlyMe, UseStart
from src.provider.error_report import send_error
from .data_source import mix_emoji

command_start = " ".join(get_driver().config.command_start)
emojis = filter(lambda e: len(e) == 1, emoji.EMOJI_DATA.keys())
emoji_pattern = "(" + "|".join(re.escape(e) for e in emojis) + ")"
pattern = re.compile(
    rf"^\s*(?P<code1>{emoji_pattern})\s*\+\s*(?P<code2>{emoji_pattern})\s*$"
)


async def check_eomjis(state: T_State, text: str = EventPlainText()) -> bool:
    text = text.strip().strip(command_start)

    if not text or "+" not in text:
        return False
    if matched := re.match(pattern, text):
        state["code1"] = matched.group("code1")
        state["code2"] = matched.group("code2")
        return True
    return False


emojimix = on_message(OnlyMe & UseStart & Rule(check_eomjis), block=False, priority=10)


@emojimix.handle()
async def _(state: T_State):
    emoji_code1 = state["code1"]
    emoji_code2 = state["code2"]

    result = await mix_emoji(emoji_code1, emoji_code2)

    if isinstance(result, str):
        return send_error(result)

    await UniMessage.image(raw=result).send()
