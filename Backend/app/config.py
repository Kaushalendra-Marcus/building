from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "BACKEND"
    VERSION: str = "1.0.0"
    ALLOWED_ORIGIN: list[str] = ["http://localhost:5173"]

    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    GROQ_API_KEY: str = Field(..., env="GROQ_API_KEY")

    PINECONE_API_KEY: str = Field(..., env="PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: str = Field(..., env="PINECONE_ENVIRONMENT")

    REDIS_URL: str = Field(..., env="REDIS_URL")

    JWT_SECRET: str = Field(..., env="JWT_SECRET")
    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    FRONTEND_URL: str = Field(..., env="FRONTEND_URL")
    
    SMTP_HOST: str = Field(..., env="SMTP_HOST")
    SMTP_PORT: int = Field(..., env="SMTP_PORT")
    SMTP_USER: str = Field(..., env="SMTP_USER")
    SMTP_PASS: str = Field(..., env="SMTP_PASS")
    EMAIL_FROM: str = Field(..., env="EMAIL_FROM")

    GOOGLE_CLIENT_ID: str = Field(..., env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field(..., env="GOOGLE_CLIENT_SECRET")

    HUGGINGFACE_MODEL_PATH: str = "sentence-transformers/all-MiniLM-L6-v2"

    UPI_ID: str = Field(..., env="UPI_ID")
    PAYMENT_AMOUNT: int = 299

    LOGIN_RATE_LIMIT: int = 5
    VERIFY_EMAIL_RATE_LIMIT: int = 3

    REQUESTS_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
