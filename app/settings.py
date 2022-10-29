import os

# settings class
from pydantic import BaseSettings


class Settings(BaseSettings):
    # app settings
    app_host: str = "0.0.0.0"
    app_port: int = 80
    app_reload: bool = False

    # database settings
    db_drivername: str
    db_user: str
    db_password: str
    db_port: int
    db_server: str
    db_db: str

    class Config:
        env_file = "local.env" if os.environ.get("LOCAL_ENV", False) else ".env"


settings = Settings()
