# Configuration settings for the application

import os

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-default-api-key")
    # Add other configuration settings as needed
    DEBUG = os.getenv("DEBUG", "False") == "True"
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///default.db")