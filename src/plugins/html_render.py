from re import findall
from asyncio import sleep

from arclet.alconna import Args, Option, Alconna, Arparma
from playwright.async_api import Page
from nonebot_plugin_alconna import Image, Match, Query, UniMessage, on_alconna
from nonebot_plugin_htmlrender import get_new_page
from nonebot.adapters.onebot.v11 import MessageEvent as V11MessageEvent
from nonebot.adapters.telegram.event import MessageEvent as TelegramMessageEvent

reg = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"


async def capture_element(
    url: str,
    element: str | None = None,
    time: float = 1,
    wait_load: bool = False,
    full_page: bool = False,
    jpeg: bool = False,
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
            return await page.locator(element).screenshot(type="jpeg" if jpeg else "png")
        else:
            return await page.screenshot(type="jpeg" if jpeg else "png", full_page=full_page)


html_render = on_alconna(
    Alconna(
        "render",
        Args["url?", str],
        Option("-i|--index", Args["index", int]),
        Option("-t|--time", Args["time", float]),
        Option("-h|--height", Args["height", int]),
        Option("-w|--width", Args["width", int]),
        Option("-f|--factor", Args["factor", float]),
        Option("-j|--jpeg"),
        Option("-a|--all"),
        Option("-e|--element", Args["element", str]),
        Option("-m"),
        Option("-l"),
    )
)


@html_render.handle()
async def _(
    res: Arparma,
    url: Match[str],
    event: V11MessageEvent | TelegramMessageEvent,
    index: Query[int] = Query("~index", 0),
    time: Query[float] = Query("~time", 3),
    width: Query[int] = Query("~width", 1280),
    height: Query[int] = Query("~height", 720),
    factor: Query[float] = Query("~factor", 2),
    full_page: Query = Query("~all"),
    element: Query[str] = Query("~element"),
    jpeg: Query = Query("~jpeg"),
):
    _url = None

    if url.available:
        _url = url.result
    else:
        # _reply: Reply = msg[Reply, 0]
        # _url = _reply.msg.extract_plain_text()
        if isinstance(event, V11MessageEvent):
            if event.reply is not None:
                _url = event.reply.message.extract_plain_text()
        elif isinstance(event, TelegramMessageEvent):
            if event.reply_to_message is not None:
                _url = event.reply_to_message.message.extract_plain_text()

    if _url is None:
        return

    if len(_url) < 3:
        return

    if len(urls := findall(reg, _url)) == 0:
        _url = "http://" + _url.strip()
    else:
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
                element.result if element.available else None,
                time=1 if res.find("l") and time.result == 3 else time.result,
                viewport={"width": width.result, "height": height.result},
                device_scale_factor=factor.result,
                is_mobile=res.find("m"),
                has_touch=res.find("m"),
                wait_load=res.find("l"),
                locale="zh-CN",
                full_page=full_page.available,
                jpeg=jpeg.available,
            ),
            mimetype="image/png",
        )
    ).send()


html_render.shortcut("必应", prefix=True, command="render https://www.bing.com/search?q={%0}")
html_render.shortcut("插件", prefix=True, command="render https://registry.nonebot.dev/search?q={%0}")
html_render.shortcut("百度", prefix=True, command="render https://www.baidu.com/s?nojc=1&wd={%0}")
html_render.shortcut("谷歌", prefix=True, command="render https://www.google.com/search?hl=zh-CN&q={%0}")
html_render.shortcut("插件", prefix=True, command="render https://registry.nonebot.dev/search?q={%0}")
