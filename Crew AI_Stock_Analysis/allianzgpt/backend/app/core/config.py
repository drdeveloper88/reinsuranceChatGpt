from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "AllianzGPT Backend"
    openai_api_key: str
    openai_api_base: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o"
    vector_db: str = "chroma"
    chroma_persist_dir: str = "./.chroma"

    jwt_secret: str = "CHANGE_ME"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
