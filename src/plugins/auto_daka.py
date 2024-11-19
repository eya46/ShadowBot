from typing import Annotated
from asyncio import gather

from nonebot import logger, get_bot, on_command
from nonebot_plugin_apscheduler import scheduler
from nonebot.adapters.onebot.v11 import Bot

from shadow.utils.send import DoFail
from src.provider.kv.utils import GetValue, get_value


@on_command("立即打卡").handle()
@scheduler.scheduled_job("cron", day="*", hour=0, name="自动群打卡")
async def _(
    bot: Bot = None,
    groups: Annotated[str, GetValue("auto_daka")] = None,
    bot_id: Annotated[str, GetValue("daka_bot_id")] = None,
):
    if groups is None:
        groups = await get_value("auto_daka")
    if bot_id is None:
        bot_id = await get_value("daka_bot_id")
    bot = get_bot(bot_id) if bot is None else bot
    if groups is None or bot_id is None or bot is None:
        try:
            await DoFail()
        except Exception as e:
            logger.error(f"打卡失败: {e}\n{groups=}\t{bot_id=}\t{bot=}")

    await gather(*[bot.call_api("set_group_sign", group_id=i) for i in map(int, groups.split(","))])
