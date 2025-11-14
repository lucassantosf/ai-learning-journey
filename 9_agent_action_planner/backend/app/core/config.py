import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "AgentFlow"
    ENVIRONMENT: str = "development"
    VERSION: str = "0.1.0"

    class Config:
        env_file = ".env"

settings = Settings()