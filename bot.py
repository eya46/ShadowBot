#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as V11Adapter

from nonebot.log import logger, default_format

logger.add(
    "log/error.log",
    rotation="00:00",
    diagnose=False,
    level="ERROR",
    format=default_format
)

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(V11Adapter)

nonebot.load_plugins("src/pre")

nonebot.load_plugin("nonebot_plugin_apscheduler")
nonebot.load_plugin("nonebot_plugin_orm")
nonebot.load_plugin("nonebot_plugin_alconna")

nonebot.load_from_toml("pyproject.toml")

nonebot.load_plugins("src/provider")
nonebot.load_plugins("src/plugins")

if __name__ == "__main__":
    nonebot.run()
