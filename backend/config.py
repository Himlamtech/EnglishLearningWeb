import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Centralized configuration management for the application."""

    # API Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "https://api.yescale.io")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4.1-nano-2025-04-14")

    # Request Configuration
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "30"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY: float = float(os.getenv("RETRY_DELAY", "1.0"))

    # Model Parameters
    DEFAULT_TEMPERATURE: float = float(os.getenv("DEFAULT_TEMPERATURE", "0.3"))
    DEFAULT_MAX_TOKENS: int = int(os.getenv("DEFAULT_MAX_TOKENS", "800"))

    # Data Storage
    DATA_DIR: str = os.path.join(os.path.dirname(__file__), "data")
    FLASHCARDS_FILE: str = os.path.join(DATA_DIR, "flashcards.csv")

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Application Settings
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration values."""
        if not cls.OPENAI_API_KEY:
            logging.warning("OPENAI_API_KEY is not set. API functionality will be limited.")
            return False
        return True

    @classmethod
    def setup_logging(cls) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL.upper()),
            format=cls.LOG_FORMAT,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(os.path.join(cls.DATA_DIR, "app.log"))
            ]
        )

# Ensure data directory exists
os.makedirs(Config.DATA_DIR, exist_ok=True)

# Setup logging
Config.setup_logging()

# Validate configuration
Config.validate()

# Legacy compatibility (to be removed in future versions)
OPENAI_API_KEY = Config.OPENAI_API_KEY
API_BASE_URL = Config.API_BASE_URL
OPENAI_MODEL = Config.OPENAI_MODEL
FLASHCARDS_FILE = Config.FLASHCARDS_FILE