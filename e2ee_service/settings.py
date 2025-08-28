from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)


class RedisSettings(BaseSettings):
    host: str = "redis"
    port: int = 6379

    model_config = SettingsConfigDict(env_prefix="REDIS_")


settings = RedisSettings()
