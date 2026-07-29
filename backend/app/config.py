from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AEGIS"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = (
        "Autonomous Enterprise Global Intelligence System"
    )

    API_PREFIX: str = "/api"

    DEBUG: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
