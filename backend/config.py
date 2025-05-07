import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.yescale.io")
OPENAI_MODEL = "gpt-4.1-nano-2025-04-14"

# Data Storage
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FLASHCARDS_FILE = os.path.join(DATA_DIR, "flashcards.csv")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True) 