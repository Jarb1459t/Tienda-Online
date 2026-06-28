from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "CiberSec 101 — Document Backend"
    app_version: str = "1.0.0"
    anthropic_api_key: str = ""
    database_url: str = "sqlite:///./cybersec101.db"
    storage_path: str = "./storage/files"
    max_file_size_mb: int = 20
    cors_origins: str = "http://localhost:3000,http://localhost:5500"

    @property
    def allowed_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def max_file_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
