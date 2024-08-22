import time

from nonebot import logger, get_bots, get_driver
from nonebot_plugin_apscheduler import scheduler
from nonebot.adapters.onebot.v11 import Bot

from src.provider.kv.utils import get_value
from shadow.utils.mcsm.client import PanelApp

superusers = get_driver().config.superusers

times = 0

driver = get_driver()


@driver.on_bot_connect
async def auto_stop(bot: Bot):
    api = await get_value("mcsm_api")
    token = await get_value("mcsm_token")
    daemon_id = await get_value("napcat_daemonId")
    instance_id = await get_value("napcat_instanceId")

    app = PanelApp(api, token)
    config = await app.api_instance(instance_id, daemon_id)
    last_time: int = config["data"]["config"]["lastDatetime"]

    if time.time() - last_time / 1000 < 60 * 5:
        # 小于5分钟判定为napcat
        logger.info("判定为napcat，不自动停止")
        return

    logger.info("判定为非napcat，自动停止")
    await app.api_protected_instance_stop(instance_id, daemon_id)


@scheduler.scheduled_job("cron", minute="*/1", name="napcat自动启动")
async def _():
    global times
    logger.debug("检查bot是否在线")
    if bots := get_bots():
        for bid in bots.keys():
            if bid in superusers:  # 在线就不启动
                return

    times += 1
    if times < 5:
        logger.info("napcat等待少于5分钟")
        return
    times = 0

    logger.debug("尝试启动napcat")

    api = await get_value("mcsm_api")
    token = await get_value("mcsm_token")
    daemon_id = await get_value("napcat_daemonId")
    instance_id = await get_value("napcat_instanceId")

    if any(i is None for i in [api, token, daemon_id, instance_id]):
        logger.error("napcat自动启动失败，缺少配置")
        return

    app = PanelApp(api, token)

    res = await app.api_protected_instance_open(instance_id, daemon_id)

    logger.info(f"napcat启动结果: [{res['status']}] {res['data']}")
