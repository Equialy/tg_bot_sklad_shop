import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class DB(BaseSettings):
    """
      Настройки для подключения к базе данных.
    """
    host: str
    port: int
    user: str
    password: str
    name: str
    scheme: str = 'public'
    provider: str = 'postgresql+asyncpg'

    @property
    def dsn(self) -> str:
        return f'{self.provider}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}'


class TgBot(BaseSettings):
    bot_token: str
    admin_id: int


class Redis(BaseSettings):
    host: str
    # db: int
    port: str
    use_redis: bool


class CSVReports(BaseSettings):
    CSV_FOLDER: str
    REPORT_FOLDER: str
    DAILY_TIME: str
    WEEKLY_DAY: str
    WEEKLY_TIME: str
    REPORT_CHAT_ID: int


class Settings(BaseSettings):
    tg_bot: TgBot
    # cache: Redis
    # reports: CSVReports
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    db: DB

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding='utf-8',
        env_nested_delimiter='__',
        case_sensitive=False,
        extra='ignore',
    )


setting = Settings()
