from typing import Annotated

from nonebot import get_bot, on_command
from nonebot_plugin_apscheduler import scheduler
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment

from src.provider.kv.utils import GetValue, get_value


@on_command("passnat").handle()
@scheduler.scheduled_job("cron", day="*", hour=0, name="passnat群自动签到")
async def _(
    bot: Bot = None,
    bot_id: Annotated[str, GetValue("daka_bot_id")] = None,
):
    group_id = 650038875
    user_id = 3889060671
    if bot_id is None:
        bot_id = await get_value("daka_bot_id")
    bot = get_bot(bot_id) if bot is None else bot

    await bot.send_group_msg(
        group_id=group_id,
        message=Message(
            [
                MessageSegment.at(user_id),
                MessageSegment.text("/checkin"),
            ]
        ),
    )
