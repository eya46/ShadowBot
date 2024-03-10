from httpx import AsyncClient
from nonebot import on_command, logger

from shadow.req import HTTPX
from src.provider.kv.utils import GetValue


@on_command("打水").handle()
async def _machine_on(
        client: AsyncClient = HTTPX(),
        token: str = GetValue("zqxy_token"),
        phone: str = GetValue("zqxy_phone"),
        sc: str = GetValue("zqxy_sc"),
        uid: str = GetValue("zqxy_uid"),
        pid: str = GetValue("zqxy_pid"),
        aid: str = GetValue("zqxy_aid")
):
    web = await client.post(
        "https://v3-api.china-qzxy.cn/order/tcpDevice/downRate/rateOrder",
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "xfModel": "0",
            "accountId": aid,
            "telPhone": phone,
            "snCode": sc,
            "phoneSystem": "android",
            "loginCode": token,
            "telephone": phone,
            "projectId": pid,
            "userId": uid,
            "version": "6.4.0.0",
        }
    )
    logger.success("water_machine_on:" + web.text)
    if (txt := web.json().get("errorMessage", web.text)) == "成功":
        return True
    logger.error(f"water_machine_on:{txt}")
