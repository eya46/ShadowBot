#!/usr/bin/env python3

from os import getenv

import nonebot
from nonebot.log import logger, default_format
from nonebot.adapters.onebot.v11 import Adapter as V11Adapter

logger.add("log/error.log", rotation="00:00", diagnose=False, level="ERROR", format=default_format)

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(V11Adapter)

nonebot.load_plugins("src/pre")
logger.success("加载完成: src/pre")

nonebot.load_plugin("nonebot_plugin_sentry")
nonebot.load_plugin("nonebot_plugin_apscheduler")
nonebot.load_plugin("nonebot_plugin_datastore")
nonebot.load_plugin("nonebot_plugin_htmlrender")
nonebot.load_plugin("nonebot_plugin_orm")
nonebot.load_plugin("nonebot_plugin_alconna")
nonebot.load_plugin("nonebot_plugin_wakatime")
logger.success("加载完成: pip/packages")

if getenv("ENVIRONMENT") != "dev":
    nonebot.load_plugin("nonebot_plugin_chatrecorder")

nonebot.load_plugins("src/provider")
logger.success("加载完成: src/provider")
nonebot.load_plugins("src/plugins")
logger.success("加载完成: src/plugins")

if __name__ == "__main__":
    nonebot.run()
