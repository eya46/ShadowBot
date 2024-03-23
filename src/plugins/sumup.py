from random import randint

from nonebot import logger, on_command
import dashscope
from nonebot.utils import run_sync
from nonebot_plugin_alconna import UniMessage
from nonebot.adapters.onebot.v11.event import MessageEvent

from shadow.exception import ActionError
from src.provider.kv.utils import GetValue

api = run_sync(dashscope.Generation.call)


@on_command("总结").handle()
async def _(event: MessageEvent, key: str = GetValue("ali_ai_key")):
    if event.reply is None:
        return await UniMessage("该命令只支持通过 回复/引用 来调用~").send()
    txt = event.reply.message.extract_plain_text()
    if len(txt) < 5:
        return await UniMessage("文本过短、经支持纯文本总结~").send()

    try:
        res = await api(
            model="qwen-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个总结文本的机器人，下面请总结用户给出的文本(不要添加额外的信息，直接给出总结)：",
                },
                {"role": "user", "content": txt},
            ],
            seed=randint(1, 99999999),
            top_p=0.8,
            result_format="message",
            enable_search=True,
            max_tokens=1500,
            temperature=0.85,
            repetition_penalty=1.0,
            api_key=key,
        )

        if res.status_code == 200:
            await UniMessage(res.message or res.output.choices[0].message.content).send()
        else:
            raise ActionError("总结失败喵~")
    except Exception as e:
        logger.exception(e)
        raise ActionError("总结失败喵~") from e
