from typing import Annotated

from nonebot import get_bot, on_command
from nonebot_plugin_apscheduler import scheduler
from nonebot.adapters.onebot.v11 import Bot

from shadow.utils.const import SUPERUSERS
from src.provider.kv.utils import GetValue, get_value


@on_command("立即打卡").handle()
@scheduler.scheduled_job("cron", day="*", hour=0, name="自动群打卡")
async def _(bot: Bot = None, groups: Annotated[str, GetValue("auto_daka")] = None):
    if bot is None:
        bot = get_bot(SUPERUSERS[0])
    if groups is None:
        groups = await get_value("auto_daka")
    for i in map(int, groups.split(",")):
        await bot.call_api("send_group_sign", group_id=i)
    return True
