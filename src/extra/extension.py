from nonebot import Bot
from pydantic import Field, BaseModel
from arclet.alconna import Alconna
from nonebot.plugin import get_plugin_config
from nonebot_plugin_alconna import Extension
from nonebot.internal.adapter import Event

from shadow.utils.const import SUPERUSERS


class Config(BaseModel):
    global_alconna_plugins_white_list: list = Field(default_factory=list)


config = get_plugin_config(Config)


class MyExtension(Extension):
    @property
    def id(self) -> str:
        return "ShadowExtension"

    @property
    def priority(self) -> int:
        return 2

    async def permission_check(self, bot: Bot, event: Event, command: Alconna) -> bool:
        if command.name in config.global_alconna_plugins_white_list:
            return True

        return event.get_user_id() in SUPERUSERS
