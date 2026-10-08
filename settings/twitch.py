from settings._base import BaseSettingsConfig

__all__ = ['TwitchSettings']


class TwitchSettings(BaseSettingsConfig, env_prefix="TWITCH_"):
    CLIENT_ID: str
    CLIENT_SECRET: str
    BOT_ID: int
    OWNER_ID: int
