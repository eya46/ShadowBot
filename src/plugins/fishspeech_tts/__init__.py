# MIT https://github.com/Cvandia/nonebot-plugin-fishspeech-tts

from nonebot import require
from nonebot.params import RegexGroup
from nonebot.plugin import on_regex, on_command

from shadow.rule import OnlyMe, UseStart, StartCommands

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import UniMessage

from .config import Config, config
from .exception import APIException
from .fish_audio_api import fish_audio_api
from .request_params import ChunkLength

chunk_length_map = {
    "normal": ChunkLength.NORMAL,
    "short": ChunkLength.SHORT,
    "long": ChunkLength.LONG,
}

chunk_length = chunk_length_map.get(config.tts_chunk_length, ChunkLength.NORMAL)


from nonebot.plugin import PluginMetadata, inherit_supported_adapters

__plugin_meta__ = PluginMetadata(
    name="FishSpeechTTS",
    description="小样本TTS,通过fish-speech调用本地或在线api发送语音",
    usage="发送:[发音人]说[文本]即可发送TTS语音",
    homepage="https://github.com/Cvandia/nonebot-plugin-fishspeech-tts",
    config=Config,
    type="application",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    extra={"author": "Cvandia", "email": "1141538825@qq.com"},
)


tts_handler = on_regex(r"(.+?)说([\s\S]*)", rule=OnlyMe & UseStart, block=False, priority=51)
balance = on_command("语音余额", block=True)

cmd_starts = " ".join(StartCommands)


@tts_handler.handle()
async def tts_handle(match: tuple = RegexGroup()):
    if not match[1]:
        await tts_handler.finish()
    text = match[1]
    speaker: str = match[0]

    request = await fish_audio_api.generate_servettsrequest(text, speaker.lstrip(cmd_starts), chunk_length)
    audio = await fish_audio_api.generate_tts(request)
    await UniMessage.voice(raw=audio).finish()


@balance.handle()
async def balance_handle():
    try:
        balance_float = await fish_audio_api.get_balance()
        await balance.finish(f"语音余额为: {balance_float}")
    except APIException as e:
        await balance.finish(str(e))
