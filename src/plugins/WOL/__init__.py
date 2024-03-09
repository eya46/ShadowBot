from typing import Annotated

from wakeonlan import send_magic_packet

from nonebot import on_command

from shadow.utils.rule import OnlyMe
from shadow.utils.send import Tap
from src.provider.kv.utils import GetValue


@on_command("开机", rule=OnlyMe).handle()
async def _(mac: Annotated[str, GetValue("wol_mac")]):
    send_magic_packet(mac)
    send_magic_packet(mac)
    await Tap()
