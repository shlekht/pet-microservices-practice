from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_PRIVATE_KEY_PATH: str = "keys/private.pem"
    JWT_ALGORITHM: str = "RS256"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()  # type: ignore
JWT_PRIVATE_KEY = Path(settings.JWT_PRIVATE_KEY_PATH).read_text()