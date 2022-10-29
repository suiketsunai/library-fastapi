import os

# settings class
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_host: str = "0.0.0.0"
    app_port: int = 80
    app_reload: bool = False

    class Config:
        env_file = "local.env" if os.environ.get("LOCAL_ENV", False) else ".env"


settings = Settings()
