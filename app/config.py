from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    COLAB_AI_URL: str
    DATABASE_URL: str
    SECRET_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
