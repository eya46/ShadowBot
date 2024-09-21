from yarl import URL
from httpx import AsyncClient
from nonebot import logger, get_bots, get_driver, on_command
from nonebot.plugin.on import on_metaevent
from nonebot_plugin_alconna import UniMessage
from nonebot_plugin_apscheduler import scheduler
from nonebot.adapters.onebot.v11 import Bot, Adapter, HeartbeatMetaEvent

from src.provider.kv.utils import get_value
from shadow.utils.mcsm.client import PanelApp

is_dev = get_driver().env == "dev"

superusers = get_driver().config.superusers

times = 0

driver = get_driver()

app: PanelApp | None = None
daemon_id: str | None = None
instance_id: str | None = None
mcsm_qq_api: str | None = None


async def get_datas():
    global app, daemon_id, instance_id, mcsm_qq_api
    if app is None:
        api = await get_value("mcsm_api")
        token = await get_value("mcsm_token")
        app = PanelApp(api, token)
    if daemon_id is None:
        daemon_id = await get_value("napcat_daemonId")
    if instance_id is None:
        instance_id = await get_value("napcat_instanceId")
    if mcsm_qq_api is None:
        mcsm_qq_api = await get_value("mcsm_qq_api")
    return app, daemon_id, instance_id, mcsm_qq_api


async def check_mcsm_qq_online() -> bool:
    _, _, _, mcsm_qq_api = await get_datas()

    if mcsm_qq_api is None:
        return False

    try:
        async with AsyncClient() as client:
            res = await client.get(str(URL(mcsm_qq_api) / "get_status"))
            data: dict = res.json()
            return data["data"]["online"]
    except:
        return False


async def check_mcsm_qq_status() -> bool:
    app, instance_id, daemon_id, _ = await get_datas()
    if app is None or instance_id is None or daemon_id is None:
        return False
    res = await app.api_instance(instance_id, daemon_id)
    return res.get("status", -1) == 3


async def restart_mcsm_qq():
    app, daemon_id, instance_id, _ = await get_datas()

    if app is None or daemon_id is None or instance_id is None:
        return

    res = await app.api_protected_instance_restart(instance_id, daemon_id)

    return res


async def start_mcsm_qq():
    app, daemon_id, instance_id, _ = await get_datas()

    if app is None or daemon_id is None or instance_id is None:
        return

    res = await app.api_protected_instance_open(instance_id, daemon_id)

    return res


async def stop_mcsm_qq():
    app, daemon_id, instance_id, _ = await get_datas()

    if app is None or daemon_id is None or instance_id is None:
        return

    res = await app.api_protected_instance_stop(instance_id, daemon_id)

    return res


@on_metaevent().handle()
async def _meta(bot: Bot, event: HeartbeatMetaEvent):
    # if not event.status.online and not is_dev:
    if not event.status.online:
        adapter: Adapter = bot.adapter
        ws = adapter.connections[bot.self_id]
        await ws.close(code=4444, reason="see you again~")


@on_metaevent().handle()
@driver.on_bot_connect
async def auto_stop(bot: Bot, event: HeartbeatMetaEvent | None = None):
    if is_dev:
        return logger.info("开发环境不自动停止")

    app, daemon_id, instance_id, _ = await get_datas()
    adapter: Adapter = bot.adapter
    ws = adapter.connections[bot.self_id]

    if event is None:
        status = await bot.get_status()
        online = status.get("online", False)
    else:
        online = event.status.online

    if await check_mcsm_qq_status():
        mcsm_qq_online = await check_mcsm_qq_online()
        if mcsm_qq_online:  # 只要mcsm qq开着但不在线就停止
            logger.info("auto_stop: mcsm qq启动但不在线，停止bot")
            await stop_mcsm_qq()
        if not online and mcsm_qq_online:  # 如果mcsm qq在线但已连bot不在线就断连(不大可能), 保证mcsm qq可以连接到bot
            logger.info("auto_stop: bot不在线且mcsm_qq在线，断连")
            await ws.close(code=4444, reason="see you again~")


@scheduler.scheduled_job("cron", minute="*/1", name="napcat自动启动")
async def auto_start():
    if is_dev:
        return logger.info("开发环境不自动启动")

    global times
    logger.debug("检查bot是否在线")
    if bots := get_bots():
        for bid, bot in bots.items():
            if isinstance(bot, Bot) and bid in superusers:  # 只处理没有bot连接的情况
                times = 0
                return

    times += 1
    if times < 5:
        logger.info("auto_start等待少于5分钟")
        return
    times = 0

    logger.debug("尝试启动mcsm qq")
    res = await start_mcsm_qq()
    if res is None:
        return logger.info("mcsm qq启动失败")
    logger.info(f"mcsm qq启动结果: [{res['status']}] {res['data']}")


@on_command("napcat").handle()
async def _napcat_handle():
    app, daemon_id, instance_id, _ = await get_datas()

    if app is None or daemon_id is None or instance_id is None:
        await UniMessage("napcat重启失败，缺少配置").finish()

    res = await start_mcsm_qq()

    await UniMessage(f"napcat启动结果: [{res['status']}] {res['data']}").send()
