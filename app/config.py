from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    groq_api_key: str = ""
    llm_model: str = "openai/gpt-oss-120b"
    db_url: str = "postgresql://sql_reader:reader_pw@localhost:5432/shop"
    max_rows: int = 100
    max_repairs: int = 2
    max_clarify_rounds: int = 2

settings = Settings()