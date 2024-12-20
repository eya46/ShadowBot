from club255 import Client
from arclet.alconna import Alconna, Subcommand, CommandMeta
from nonebot.exception import FinishedException
from nonebot_plugin_alconna import UniMessage, on_alconna

from shadow.utils.const import Undefined
from src.provider.kv.utils import GetValue, add_kv

_255 = on_alconna(
    Alconna("255", Subcommand("签到"), Subcommand("补签"), Subcommand("登录"), meta=CommandMeta(compact=True))
)


@_255.assign("登录")
async def _login(
    url: str = GetValue("255_url"),
    account: str = GetValue("255_account"),
    password: str = GetValue("255_password"),
    token: str | None = GetValue("255_token", fail_tip=Undefined),
):
    client = Client(url, account, password, token)
    try:
        if await client.check_token():
            await UniMessage("已登录").finish()

        login_info = await client.login()

        if login_info.code == 0:
            await UniMessage("登录成功").finish()
        await UniMessage(f"登录失败: {login_info.msg}").finish()
    except FinishedException:
        raise
    except Exception as e:
        await UniMessage(f"登录失败: {e}").send()
    finally:
        await add_kv("255_token", client.get_token())


@_255.assign("签到")
async def _sign(
    url: str = GetValue("255_url"),
    account: str = GetValue("255_account"),
    password: str = GetValue("255_password"),
    token: str | None = GetValue("255_token", fail_tip=Undefined),
):
    client = Client(url, account, password, token)
    try:
        if not await client.check_token():
            login_info = await client.login()
            if login_info.code != 0:
                await UniMessage(f"登录失败: {login_info.msg or '未知原因'}").finish()

        if_sign = await client.check_if_sign()

        if if_sign:
            await UniMessage("已签到").finish()

        sign_info = await client.sign_now()

        if sign_info.code == 0:
            await UniMessage(f"签到成功<exp:{sign_info.exp}>:\n{sign_info.msg}").finish()

        await UniMessage(f"签到失败: {sign_info.msg}").send()
    finally:
        await add_kv("255_token", client.get_token())


@_255.assign("补签")
async def _resign(
    url: str = GetValue("255_url"),
    account: str = GetValue("255_account"),
    password: str = GetValue("255_password"),
    token: str | None = GetValue("255_token", fail_tip=Undefined),
):
    client = Client(url, account, password, token)
    try:
        if not await client.check_token():
            login_info = await client.login()
            if login_info.code != 0:
                await UniMessage(f"登录失败: {login_info.msg or '未知原因'}").finish()

        resign_info = await client.sign_fill()
        if resign_info.code == 0:
            await UniMessage(f"补签成功:\n{resign_info.msg}").finish()
        await UniMessage(f"补签失败: {resign_info.msg}").send()
    finally:
        await add_kv("255_token", client.get_token())
