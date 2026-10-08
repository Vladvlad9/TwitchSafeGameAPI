from settings._base import BaseSettingsConfig

__all__ = ['AppSettings']


class AppSettings(BaseSettingsConfig, env_prefix="APP_"):
    ENV: str
    PROJECT_NAME: str
    VERSION: str
