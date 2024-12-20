from httpx import AsyncClient
import ormsgpack
from nonebot.log import logger

from .config import config
from .exception import (
    APIException,
    HTTPException,
    AuthorizationException,
)
from .request_params import ChunkLength, ServeTTSRequest


class FishAudioAPI:
    """
    FishAudioAPI类, 用于调用FishAudio的API接口
    """

    def __init__(self):
        self.url = "https://api.fish.audio/v1/tts"

        # 如果在线授权码为空, 且使用在线api, 则抛出异常
        if not config.online_authorization:
            raise APIException("请先在配置文件中填写在线授权码或使用离线api")
        else:
            self.headers = {
                "Authorization": f"Bearer {config.online_authorization}",
            }

    async def _get_reference_id_by_speaker(self, speaker: str) -> str:
        """
        通过说话人姓名获取说话人的reference_id

        Args:
            speaker: 说话人姓名

        Returns:
            reference_id: 说话人的reference_id

        exception:
            APIException: 获取语音角色列表为空
        """
        request_api = "https://api.fish.audio/model"
        async with AsyncClient() as client:
            params = {"title": speaker}
            response = await client.get(request_api, params=params, headers=self.headers)
            resp_data = response.json()
            if resp_data["total"] == 0:
                raise APIException("获取语音角色列表为空")
            else:
                return resp_data["items"][0]["_id"]

    async def generate_servettsrequest(
        self,
        text: str,
        speaker_name: str,
        chunk_length: ChunkLength = ChunkLength.NORMAL,
    ) -> ServeTTSRequest:
        """
        生成TTS请求

        Args:
            text: 待合成文本
            speaker_name: 说话人姓名
            chunk_length: 分片长度

        Returns:
            ServeTTSRequest: TTS请求
        """
        try:
            reference_id = await self._get_reference_id_by_speaker(speaker_name)
        except APIException as e:
            raise e
        return ServeTTSRequest(
            text=text,
            reference_id=reference_id,
            format="wav",
            mp3_bitrate=64,
            latency="normal",
            opus_bitrate=24,
            normalize=True,
            chunk_length=chunk_length.value,
        )

    async def generate_tts(self, request: ServeTTSRequest) -> bytes:
        """
        获取TTS音频

        Args:
            request: TTS请求

        Returns:
            bytes: TTS音频二进制数据
        """
        if request.references:
            self.headers["content-type"] = "application/msgpack"
            try:
                async with AsyncClient() as client:
                    async with client.stream(
                        "POST",
                        self.url,
                        headers=self.headers,
                        content=ormsgpack.packb(request, option=ormsgpack.OPT_SERIALIZE_PYDANTIC),
                    ) as resp:
                        return await resp.aread()
            except HTTPException as e:
                logger.error(f"获取TTS音频失败: {e}")
                raise APIException("网络错误, 请检查网络连接")
        else:
            self.headers["content-type"] = "application/json"
            try:
                async with AsyncClient() as client:
                    response = await client.post(
                        self.url,
                        headers=self.headers,
                        json=request.dict(),
                        timeout=60,
                    )
                    return response.content
            except HTTPException as e:
                logger.error(f"获取TTS音频失败: {e}")
                raise APIException("网络错误, 请检查网络连接")

    async def get_balance(self) -> float:
        """
        获取账户余额
        """
        balance_url = "https://api.fish.audio/wallet/self/api-credit"
        async with AsyncClient() as client:
            response = await client.get(balance_url, headers=self.headers)
            try:
                return response.json()["credit"]
            except KeyError:
                raise AuthorizationException("授权码错误或已失效")


fish_audio_api = FishAudioAPI()
