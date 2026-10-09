from pathlib import Path
from typing import Annotated

from pydantic import Field

from settings._base import BaseSettingsConfig
from settings.app import AppSettings
from settings.redis import RedisSettings
from settings.server import ServerSettings
from settings.twitch import TwitchSettings

__all__ = ['settings']


class Settings(BaseSettingsConfig):
    BASE_DIR: Path = Path(__file__).parent.parent

    SERVER: Annotated[ServerSettings, Field(default_factory=ServerSettings)]
    APP: Annotated[AppSettings, Field(default_factory=AppSettings)]
    REDIS: Annotated[RedisSettings, Field(default_factory=RedisSettings)]
    TWITCH: Annotated[TwitchSettings, Field(default_factory=TwitchSettings)]


settings = Settings()
