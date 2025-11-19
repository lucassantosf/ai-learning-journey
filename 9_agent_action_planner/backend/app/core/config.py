from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pydantic import Field

load_dotenv()

class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field("gpt-4o-mini", env="OPENAI_MODEL")

    # SQLite / Database
    DATABASE_URL: str = Field("sqlite:///./memory.db", env="DATABASE_URL")

    class Config:
        env_file = ".env"

settings = Settings() 
