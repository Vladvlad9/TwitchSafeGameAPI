from pydantic import RedisDsn

from settings._base import BaseSettingsConfig

__all__ = ["RedisSettings"]


class RedisSettings(BaseSettingsConfig, env_prefix="REDIS_"):
    DSN: RedisDsn
