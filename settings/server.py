from pydantic import PositiveInt

from settings._base import BaseSettingsConfig

__all__ = ['ServerSettings']


class ServerSettings(BaseSettingsConfig, env_prefix='SERVER_'):
    HOST: str
    PORT: PositiveInt
