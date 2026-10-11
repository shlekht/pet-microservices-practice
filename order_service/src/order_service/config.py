from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    RABBITMQ_URL: str

    payment_exchange_name: str = "payment.events"
    payment_succeeded_routing_key: str = "payment.succeeded"
    payment_queue_name: str = "payment.results"
    PAYMENT_API_URL: str = "http://localhost:8001"

    JWT_PUBLIC_KEY_PATH: str = "keys/public.pem"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()  # type: ignore
JWT_PUBLIC_KEY = Path(settings.JWT_PUBLIC_KEY_PATH).read_text()