# MIT
# https://github.com/noneplugin/nonebot-plugin-simplemusic

from typing import Any, Protocol
import asyncio
from difflib import SequenceMatcher
import traceback
from dataclasses import dataclass

import httpx
from nonebot import on_command
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.typing import T_Handler
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Message, MessageSegment


async def search_qq(keyword: str) -> MessageSegment | None:
    url = "https://c.y.qq.com/splcloud/fcgi-bin/smartbox_new.fcg"
    params = {
        "format": "json",
        "inCharset": "utf-8",
        "outCharset": "utf-8",
        "notice": 0,
        "platform": "yqq.json",
        "needNewCode": 0,
        "uin": 0,
        "hostUin": 0,
        "is_xml": 0,
        "key": keyword,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        result = resp.json()
    songs: list[dict[str, str]] = result["data"]["song"]["itemlist"]
    if songs:
        songs.sort(
            key=lambda x: SequenceMatcher(None, keyword, x["name"]).ratio(),
            reverse=True,
        )
        return MessageSegment.music("qq", int(songs[0]["id"]))


async def search_163(keyword: str) -> MessageSegment | None:
    url = "https://music.163.com/api/cloudsearch/pc"
    params = {"s": keyword, "type": 1, "offset": 0}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, params=params)
        result = resp.json()
    songs: list[dict[str, Any]] = result["result"]["songs"]
    if songs:
        songs.sort(
            key=lambda x: SequenceMatcher(None, keyword, x["name"]).ratio(),
            reverse=True,
        )
        return MessageSegment.music("163", songs[0]["id"])


async def search_kuwo(keyword: str) -> MessageSegment | None:
    search_url = "https://search.kuwo.cn/r.s"
    params = {
        "all": keyword,
        "pn": 0,
        "rn": 1,
        "ft": "music",
        "rformat": "json",
        "encoding": "utf8",
        "pcjson": "1",
        "vipver": "MUSIC_9.1.1.2_BCS2",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(search_url, params=params)
        result = resp.json()

        songs: list[dict[str, Any]] = result["abslist"]
        if songs:
            songs.sort(
                key=lambda x: SequenceMatcher(None, keyword, x["SONGNAME"]).ratio(),
                reverse=True,
            )

            rid = str(songs[0]["MUSICRID"]).strip("MUSIC_")
            song_url = "http://m.kuwo.cn/newh5/singles/songinfoandlrc"
            params = {"musicId": rid, "httpsStatus": 1}
            resp = httpx.get(song_url, params=params)
            result = resp.json()

            if info := result["data"]["songinfo"]:
                play_url = "https://kuwo.cn/api/v1/www/music/playUrl"
                params = {
                    "mid": rid,
                    "type": "convert_url3",
                    "httpsStatus": 1,
                    "br": "128kmp3",
                }
                resp = httpx.get(play_url, params=params)
                result: dict = resp.json()

                if data := result.get("data"):
                    return MessageSegment(
                        "music",
                        {
                            "type": "custom",
                            "subtype": "kuwo",
                            "url": f"https://kuwo.cn/play_detail/{rid}",
                            "voice": data["url"],
                            "title": info["songName"],
                            "content": info["artist"],
                            "image": info["pic"],
                        },
                    )


async def search_kugou(keyword: str) -> MessageSegment | None:
    search_url = "http://mobilecdn.kugou.com/api/v3/search/song"
    params = {
        "format": "json",
        "keyword": keyword,
        "showtype": 1,
        "page": 1,
        "pagesize": 1,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(search_url, params=params)
        result = resp.json()

        songs: list[dict[str, Any]] = result["data"]["info"]
        if songs:
            songs.sort(
                key=lambda x: SequenceMatcher(None, keyword, x["songname"]).ratio(),
                reverse=True,
            )

            hash = songs[0]["hash"]
            album_id = songs[0]["album_id"]
            song_url = "http://m.kugou.com/app/i/getSongInfo.php"
            params = {"cmd": "playInfo", "hash": hash}
            resp = await client.get(song_url, params=params)

            if info := resp.json():
                return MessageSegment(
                    "music",
                    {
                        "type": "custom",
                        "subtype": "kugou",
                        "url": f"https://www.kugou.com/song/#hash={hash}&album_id={album_id}",
                        "voice": info["url"],
                        "title": info["songName"],
                        "content": info["author_name"],
                        "image": str(info["imgUrl"]).format(size=240),
                    },
                )


async def search_migu(keyword: str) -> MessageSegment | None:
    url = "https://m.music.migu.cn/migu/remoting/scr_search_tag"
    params = {"rows": 1, "type": 2, "keyword": keyword, "pgc": 1}
    headers = {"Referer": "https://m.music.migu.cn"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, headers=headers)
        result = resp.json()
    songs: list[dict[str, Any]] = dict(result).get("musics", [])
    if songs:
        songs.sort(
            key=lambda x: SequenceMatcher(None, keyword, x["title"]).ratio(),
            reverse=True,
        )
        info = songs[0]
        return MessageSegment(
            "music",
            {
                "type": "custom",
                "subtype": "migu",
                "url": f"https://music.migu.cn/v3/music/song/{info['copyrightId']}",
                "voice": info["mp3"],
                "title": info["title"],
                "content": info["singerName"],
                "image": info["cover"],
            },
        )


async def search_bili(keyword: str) -> MessageSegment | None:
    search_url = "https://api.bilibili.com/audio/music-service-c/s"
    params = {"page": 1, "pagesize": 1, "search_type": "music", "keyword": keyword}
    async with httpx.AsyncClient() as client:
        resp = await client.get(search_url, params=params)
        result = resp.json()
    songs: list[dict[str, Any]] = result["data"]["result"]
    if songs:
        songs.sort(
            key=lambda x: SequenceMatcher(None, keyword, x["title"]).ratio(),
            reverse=True,
        )
        info = songs[0]
        return MessageSegment.text(f"https://www.bilibili.com/audio/au{info['id']}")


class Func(Protocol):
    async def __call__(self, keyword: str) -> MessageSegment | None: ...


@dataclass
class Source:
    name: str
    keywords: tuple[str, ...]
    func: Func


sources = [
    Source("网易云音乐", ("163点歌", "网易点歌", "网易云点歌"), search_163),
    Source("QQ音乐", ("qq点歌", "QQ点歌"), search_qq),
    Source("酷我音乐", ("kuwo点歌", "酷我点歌"), search_kuwo),
    Source("酷狗音乐", ("kugou点歌", "酷狗点歌"), search_kugou),
    Source("咪咕音乐", ("migu点歌", "咪咕点歌"), search_migu),
    Source("B站音频区", ("bili点歌", "bilibili点歌", "b站点歌", "B站点歌"), search_bili),
]


def retry(func: Func, count=3, sleep=3):
    async def wrapper(*args, **kwargs):
        for i in range(count):
            try:
                res = await func(*args, **kwargs)
                return res
            except:
                if i >= count - 1:
                    raise
                await asyncio.sleep(sleep)

    return wrapper


def create_matchers():
    def create_handler(source: Source) -> T_Handler:
        async def handler(matcher: Matcher, msg: Message = CommandArg()):
            keyword = msg.extract_plain_text().strip()
            if not keyword:
                matcher.block = False
                await matcher.finish()

            try:
                res = await retry(source.func)(keyword)
                if not res:
                    res = f"{source.name}中找不到相关的歌曲"
            except Exception:
                logger.warning(traceback.format_exc())
                res = "出错了，请稍后再试"
            if res:
                return True

        return handler

    for source in sources:
        on_command(source.keywords[0], aliases=set(source.keywords), block=True, priority=12).append_handler(
            create_handler(source)
        )


create_matchers()


async def handler(matcher: Matcher, msg: Message = CommandArg()):
    keyword = msg.extract_plain_text().strip()
    if not keyword:
        matcher.block = False
        await matcher.finish()

    res = None
    for source in sources:
        try:
            res = await source.func(keyword)
        except:
            pass
        if res:
            await matcher.finish(res)
    if not res:
        return True


on_command("点歌", block=True, priority=12).append_handler(handler)
