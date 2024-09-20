from nonebot import logger, get_bots, get_driver, on_command
from nonebot_plugin_alconna import UniMessage
from nonebot_plugin_apscheduler import scheduler
from nonebot.adapters.onebot.v11 import Bot

from src.provider.kv.utils import get_value
from shadow.utils.mcsm.client import PanelApp

is_dev = get_driver().env == "dev"

superusers = get_driver().config.superusers

times = 0

driver = get_driver()


@on_command("napcat").handle()
async def _napcat_handle():
    api = await get_value("mcsm_api")
    token = await get_value("mcsm_token")
    daemon_id = await get_value("napcat_daemonId")
    instance_id = await get_value("napcat_instanceId")

    if any(i is None for i in [api, token, daemon_id, instance_id]):
        logger.error("napcat重启失败，缺少配置")
        return

    app = PanelApp(api, token)

    res = await app.api_protected_instance_restart(instance_id, daemon_id)

    await UniMessage(f"napcat启动结果: [{res['status']}] {res['data']}").send()


@driver.on_bot_connect
async def auto_stop(bot: Bot):
    if is_dev:
        return logger.info("开发环境不自动停止")

    api = await get_value("mcsm_api")
    token = await get_value("mcsm_token")
    daemon_id = await get_value("napcat_daemonId")
    instance_id = await get_value("napcat_instanceId")

    app = PanelApp(api, token)

    info = await bot.get_version_info()

    if info.get("app_name") == "NapCat.Onebot":
        logger.info("判断为NapCat.Onebot, 不自动停止")
        return

    logger.info("判断为PC上线, 自动停止")
    await app.api_protected_instance_stop(instance_id, daemon_id)


@scheduler.scheduled_job("cron", minute="*/1", name="napcat自动启动")
async def _():
    if is_dev:
        return logger.info("开发环境不自动启动")

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


@scheduler.scheduled_job("cron", minute="*/1", name="napcat自动关闭")
async def __():
    if is_dev:
        return logger.info("开发环境不自动关闭")

    bots = get_bots()

    for bid, bot in bots.items():
        if bid not in superusers:
            continue

        info = await bot.get_version_info()

        # 只有NapCat才检测是否离线
        if info.get("app_name") != "NapCat.Onebot":
            continue

        try:
            data: list = await bot.call_api("get_robot_uin_range")
            # 离线状态下返回空列表/超时
            if len(data) != 0:
                continue
        except Exception as e:
            logger.error(f"在线测试失败: [{type(e)}]{e}")

        api = await get_value("mcsm_api")
        token = await get_value("mcsm_token")
        daemon_id = await get_value("napcat_daemonId")
        instance_id = await get_value("napcat_instanceId")

        app = PanelApp(api, token)
        await app.api_protected_instance_stop(instance_id, daemon_id)
