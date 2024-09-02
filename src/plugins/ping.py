from nonebot import on_command

from shadow.utils.send import DoSuccess


@on_command("ping").handle()
async def _():
    await DoSuccess()
