from typing import Annotated

from nonebot import on_command
from wakeonlan import send_magic_packet

from shadow.utils.send import DoSuccess
from src.provider.kv.utils import GetValue


@on_command("开机").handle()
async def _(mac: Annotated[str, GetValue("wol_mac")]):
    send_magic_packet(mac)
    send_magic_packet(mac)
    await DoSuccess()
