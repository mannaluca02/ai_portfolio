
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application Settings
    Loads configuration from environment variables
    """

    # Database
    DATABASE_URL: str

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = Field(default=300, ge=100, le=1000)
    OPENAI_TIMEOUT_SECONDS: float = Field(default=15, gt=0, le=25)
    CHAT_MAX_CONCURRENT: int = Field(default=2, ge=1, le=8)

    # Embedding Model
    BGE_MODEL_PATH: str = "./app/ml_models/bge-m3"
    BGE_MODEL_NAME: str = "BAAI/bge-m3"

    # Rate Limiting (centralized configuration)
    # Natural Mode (LLM-powered chatbot)
    RATE_LIMIT_NATURAL_DAILY: int = 20  # Max requests per day per IP
    RATE_LIMIT_NATURAL_MONTHLY: int = 100  # Max requests per month per IP

    # Listen Mode (search-only, no LLM)
    RATE_LIMIT_LISTEN_DAILY: int = 40  # Max requests per day per IP
    RATE_LIMIT_LISTEN_MONTHLY: int = 200  # Max requests per month per IP

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # Verification
    SKIP_VERIFICATION: bool = False
    VERIFICATION_THRESHOLD: float = Field(default=0.6, ge=0.6, le=1.0)

    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
