from os import getcwd
from typing import Literal, Optional

from playwright.async_api import Page


async def html_to_pic(
        page: Page,
        html: str,
        wait: int = 0,
        template_path: str = f"file://{getcwd()}",
        type_: Literal["jpeg", "png"] = "png",
        quality: Optional[int] = None,
) -> bytes:
    if not template_path.startswith("file://"):
        raise Exception("template_path 应该为 file://...")
    await page.goto(template_path)
    await page.set_content(html, wait_until="networkidle")
    await page.wait_for_timeout(wait)
    return await page.screenshot(
        full_page=True,
        type=type_,
        quality=quality,
    )
