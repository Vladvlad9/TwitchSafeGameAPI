from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ['BaseSettingsConfig']


class BaseSettingsConfig(BaseSettings):
    model_config = SettingsConfigDict(
        frozen=True,
        case_sensitive=False,
        str_strip_whitespace=True,
        coerce_numbers_to_str=True,
        use_enum_values=True,
    )
