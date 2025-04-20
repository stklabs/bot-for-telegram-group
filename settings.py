from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    prize_amount: int = 1000  # SATS
    draw_time: int = 20
    draw_day: int = 4  # De 0 - 6 onde 0 é Segunda e 6 é Domingo
    BOT_TOKEN: str
    CHAT_ID: str
    nwc_uri: str
    DEV_MODE: bool = False


setup = Settings()
