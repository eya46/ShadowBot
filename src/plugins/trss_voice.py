from typing import Annotated
from urllib.parse import quote

from yarl import URL
from nonebot import get_driver, on_message
from nonebot.rule import Rule
from nonebot.params import T_State, EventPlainText
from nonebot.matcher import Matcher
from nonebot.internal.adapter import Event
from nonebot.adapters.onebot.v11 import MessageSegment

from shadow.rule import OnlyMe, UseStart
from shadow.exception import ActionError
from src.provider.kv.utils import GetValue

command_start = " ".join(get_driver().config.command_start)

speakers = [
    "派蒙",
    "凯亚",
    "安柏",
    "丽莎",
    "琴",
    "香菱",
    "枫原万叶",
    "迪卢克",
    "温迪",
    "可莉",
    "早柚",
    "托马",
    "芭芭拉",
    "优菈",
    "云堇",
    "钟离",
    "魈",
    "凝光",
    "雷电将军",
    "北斗",
    "甘雨",
    "七七",
    "刻晴",
    "神里绫华",
    "戴因斯雷布",
    "雷泽",
    "神里绫人",
    "罗莎莉亚",
    "阿贝多",
    "八重神子",
    "宵宫",
    "荒泷一斗",
    "九条裟罗",
    "夜兰",
    "珊瑚宫心海",
    "五郎",
    "散兵",
    "女士",
    "达达利亚",
    "莫娜",
    "班尼特",
    "申鹤",
    "行秋",
    "烟绯",
    "久岐忍",
    "辛焱",
    "砂糖",
    "胡桃",
    "重云",
    "菲谢尔",
    "诺艾尔",
    "迪奥娜",
    "鹿野院平藏",
]


async def split(state: T_State, text: str = EventPlainText()) -> bool:
    text = text.strip().strip(command_start)
    _ = text.split("说", 1)
    if len(_) != 2:
        return False
    if _[0] not in speakers:
        state["speaker"] = None
        state["text"] = None
    else:
        state["speaker"] = speakers.index(_[0])
        state["text"] = _[1]
    return True


@on_message(rule=(OnlyMe & UseStart & Rule(split)), block=False, priority=50).handle()
async def _(event: Event, matcher: Matcher, state: T_State, voice_api: Annotated[str, GetValue("voice_api")]):
    speaker: int = state["speaker"]
    text: str = state["text"]

    if speaker is None or text is None:
        raise ActionError("无法识别发言者")

    await matcher.send(
        MessageSegment.record(
            str(
                URL(voice_api)
                / f"?user_id={event.get_user_id()}&bot_id={event.get_user_id()}&id={speaker}&text={quote(text)}"
            )
        )
    )
