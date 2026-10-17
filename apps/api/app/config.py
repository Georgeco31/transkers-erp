from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Transker ERP API"
    database_url: str = "sqlite:///./transker.db"
    secret_key: str = Field(default="development-secret-key-change-before-production", min_length=32)
    access_token_expire_minutes: int = 480
    admin_username: str = "admin"
    admin_password: str = "admin12345"
    cookie_secure: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

