
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "BloodLife API"
    APP_VERSION: str = "1.0.0"

    # Database configuration
    DATABASE_URL: str | None = None

    # Security configuration
    SECRET_KEY: str = "change-this-secret-key-before-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
