from re import findall
from asyncio import sleep

from arclet.alconna import Args, Option, Alconna, Arparma
from playwright.async_api import Page
from nonebot_plugin_alconna import Image, Match, Query, UniMsg, UniMessage, on_alconna
from nonebot_plugin_htmlrender import get_new_page
from nonebot.adapters.onebot.v11 import MessageEvent

reg = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"


async def capture_element(
        url: str,
        element: str | None = None,
        time: float = 1,
        wait_load: bool = False,
        **kwargs,
) -> bytes:
    async with get_new_page(**kwargs) as page:
        page: Page
        await page.goto(url)
        if wait_load:
            try:
                await page.wait_for_load_state("load")
            except:
                raise Exception("等待加载超时")
        await sleep(time)
        if element:
            return await page.locator(element).screenshot(type="png")
        else:
            return await page.screenshot(type="png")


@on_alconna(
    Alconna(
        "render",
        Args["url?", str],
        Option("-i|--index", Args["index", int]),
        Option("-t|--time", Args["time", float]),
        Option("-h|--height", Args["height", int]),
        Option("-w|--width", Args["width", int]),
        Option("-f|--factor", Args["factor", float]),
        Option("-m"),
        Option("-l"),
    )
).handle()
async def _(
        res: Arparma,
        url: Match[str], msg: UniMsg, event: MessageEvent, index: Query[int] = Query("~index", 0),
        time: Query[float] = Query("~time", 3), width: Query[int] = Query("~width", 1280),
        height: Query[int] = Query("~height", 720), factor: Query[float] = Query("~factor", 2),

):
    if not url.available and event.reply is None:
        return

    _url = None

    if url.available:
        _url = url.result
    else:
        # _reply: Reply = msg[Reply, 0]
        # _url = _reply.msg.extract_plain_text()
        _url = event.reply.message.extract_plain_text()

    urls = findall(reg, _url)

    if len(urls) == 0:
        raise Exception("未找到链接")

    if index.available:
        if index.result >= len(urls):
            raise Exception("索引超出范围")
        _url = urls[index.result]
    else:
        _url = urls[0]

    await UniMessage(
        Image(
            raw=await capture_element(
                _url,
                "body",
                time=1 if res.find("l") and time.result == 3 else time.result,
                viewport={"width": width.result, "height": height.result},
                device_scale_factor=factor.result,
                is_mobile=res.find("m"),
                has_touch=res.find("m"),
                wait_load=res.find("l"),
            ),
            mimetype="image/png"
        )
    ).send()
