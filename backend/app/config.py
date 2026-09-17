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
    # Chosen by measurement over the twelve production-log questions, three
    # passes each: gpt-4o-mini cites every sentence in 75 percent of answers
    # against gpt-3.5-turbo's 58 percent, at a 1129 ms median instead of 2079 ms.
    # gpt-4.1-mini cites slightly better (86 percent) but is 43 percent slower
    # with the same verified rate; gpt-5-mini needs 14.7 s. The gpt-5 family also
    # rejects max_tokens, so switching there needs a client change, not only this.
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_MAX_TOKENS: int = Field(default=300, ge=100, le=1000)
    OPENAI_TIMEOUT_SECONDS: float = Field(default=15, gt=0, le=25)
    CHAT_MAX_CONCURRENT: int = Field(default=2, ge=1, le=8)

    # Embedding Model
    BGE_MODEL_PATH: str = "./app/ml_models/bge-m3"
    BGE_MODEL_NAME: str = "BAAI/bge-m3"
    # Threads for torch's intra-op pool. 0 reads the container's CPU quota from
    # the cgroup, which is the right default: torch otherwise sizes the pool
    # from the host's cores and oversubscribes a fraction of a core. Set this by
    # hand only where the cgroup reports no quota.
    TORCH_NUM_THREADS: int = Field(default=0, ge=0, le=64)

    # Rate Limiting (centralized configuration)
    # Natural Mode (LLM-powered chatbot)
    # Raised with the mini-model swap: an answer costs a fraction of a cent, and
    # 20 per day per IP cut off real visitors on a public portfolio.
    RATE_LIMIT_NATURAL_DAILY: int = 50  # Max requests per day per IP
    RATE_LIMIT_NATURAL_MONTHLY: int = 400  # Max requests per month per IP

    # Listen Mode (search-only, no LLM)
    RATE_LIMIT_LISTEN_DAILY: int = 40  # Max requests per day per IP
    RATE_LIMIT_LISTEN_MONTHLY: int = 200  # Max requests per month per IP

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # Verification
    SKIP_VERIFICATION: bool = False
    # Calibrated on the live corpus (backend/scripts/calibrate_verifier.py),
    # re-measured 2026-09-13 after re-embedding: 0.55 accepts all 8 supported
    # German paraphrases, the weakest at 0.565, and rejects all 7 unsupported
    # ones, the strongest at 0.485. 0.60 rejects three true claims. The lower
    # bound keeps the check meaningful if this is ever tuned by hand.
    VERIFICATION_THRESHOLD: float = Field(default=0.55, ge=0.4, le=1.0)

    # Application
    # Provisional English settings: retain the German values until measured.
    VERIFICATION_THRESHOLD_EN: float = Field(default=0.55, ge=0.4, le=1.0)
    EXCERPT_FLOOR_EN: float = Field(default=0.40, ge=0.0, le=1.0)
    EXCERPT_GAP_EN: float = Field(default=0.03, ge=0.0, le=1.0)

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
