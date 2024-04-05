from nonebot import on_command
from nonebot.exception import FinishedException
from nonebot_plugin_alconna import UniMessage
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent


@on_command("url").handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if (replay := event.reply) is None:
        raise FinishedException
    message = replay.message
    urls = []
    for i in message:
        if i.type == "file":
            resp = await bot.call_api(
                "get_group_file_url",
                group_id=event.group_id,
                file_id=i.data.get("file_id"),
                busid=i.data.get("busid"),
                fname=i.data.get("name")
            )
            urls.append(resp.url)

    await UniMessage("\n\n".join(urls)).send()
