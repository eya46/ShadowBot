from random import randint

from arclet.alconna import Args, Option, Alconna
from nonebot import logger, on_command
from nonebot_plugin_alconna import Query, UniMsg, UniMessage, on_alconna

from shadow.exception import ActionError
from src.provider.kv.utils import GetValue
from .util import ai_caller, check_msg_type

sum_up = on_alconna(
    Alconna(
        "总结",
        Option("-p|--prompt", Args["prompt", str]),
        Option("-r|--raw", Args["raw", str]),
    )
)


@on_command("总结").handle()
async def _(
        msg: UniMsg, raw_prompt: Query[str] = Query("~prompt", ""),
        key: str = GetValue("ali_ai_key")
):
    type_, data_ = await check_msg_type(msg)

    if type_ == "text":
        text, prompt = data_
        prompt = prompt or raw_prompt.result

        try:
            res = await ai_caller(
                model="qwen-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"你是一个总结文本的机器人，下面请总结用户给出的文本，并且{prompt}(不要添加额外的信息，直接给出总结)："
                        if prompt
                        else "你是一个总结文本的机器人，下面请总结用户给出的文本(不要添加额外的信息，直接给出总结)：",
                    },
                    {"role": "user", "content": text},
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
