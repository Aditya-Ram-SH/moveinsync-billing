from functools import lru_cache
from typing import List, Optional

from pydantic import PostgresDsn

try:
    from pydantic_settings import BaseSettings
except ImportError as exc:
    raise ImportError(
        "pydantic-settings is required. Install it with `pip install pydantic-settings`."
    ) from exc


class Settings(BaseSettings):
    PROJECT_NAME: str = "MoveInSync Billing API"
    API_PREFIX: str = "/api"

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str = "password123"
    POSTGRES_DB: str = "moveinsync_db"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    SECRET_KEY: str = "super-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    JWT_ALGORITHM: str = "HS256"

    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    class Config:
        env_file = ".env"

    @property
    def database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return str(self.SQLALCHEMY_DATABASE_URI)
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

