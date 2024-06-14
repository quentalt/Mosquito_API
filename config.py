from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_URL: str
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env")
