import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    gemini_api_key: str
    debug: bool = False
    log_level: str = "INFO"
    data_dir: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Khởi tạo Singleton instance của cấu hình
settings = Settings()
