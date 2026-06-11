from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost/notes_db"
    REDIS_URL: str = "redis://localhost:6379/0"    OPENAI_API_KEY: str = ""

    class Config:
        env_file = ".env"

    # Security settings for JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Rate limit settings (strings used by SlowAPI decorators)
    GRAMMAR_RATE: str = "5/minute"
    WRITE_RATE: str = "20/minute"

settings = Settings()
