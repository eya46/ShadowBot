from pydantic import BaseModel
from typing import Optional, Literal
from nonebot import get_plugin_config


class Config(BaseModel):
    tts_chunk_length: Literal["normal", "short", "long"] = "normal"
    # 区分配置
    online_authorization: Optional[str] = "xxxxx"


config = get_plugin_config(Config)
