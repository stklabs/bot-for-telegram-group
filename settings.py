from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    prize_amount: int = 100  # SATS
    BOT_TOKEN: str
    CHAT_ID: str
    nwc_uri: str
    DEV_MODE: bool = False


setup = Settings()
