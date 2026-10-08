from pydantic import PositiveInt

from settings._base import BaseSettingsConfig

__all__ = ['TwitchSettings']


class TwitchSettings(BaseSettingsConfig, env_prefix="TWITCH_"):
    CLIENT_ID: str
    CLIENT_SECRET: str
    BOT_ID: str
    OWNER_ID: str
    OAUTH_HOST: str = "0.0.0.0"
    OAUTH_PORT: PositiveInt = 4343
    REDIRECT_URI: str = "http://localhost:4343/oauth/callback"
