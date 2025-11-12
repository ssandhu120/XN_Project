"""Configuration management for the XN Mental Health Chatbot."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration settings."""
    
    # API Keys (optional)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # Application Settings
    APP_TITLE: str = "MindBridge Care - Mental Health Support"
    APP_DESCRIPTION: str = "Personalized mental health guidance for college students"
    
    # Crisis Contact Information
    CRISIS_HOTLINE: str = "988 (Suicide & Crisis Lifeline)"
    NORTHEASTERN_COUNSELING: str = "(617) 373-2772"
    EMERGENCY_NUMBER: str = "911"
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "xn_chatbot.log")
    
    # LLM Configuration
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "500"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Session Configuration
    MAX_CONVERSATION_LENGTH: int = 50
    SESSION_TIMEOUT_MINUTES: int = 30
    
    # Feature Flags
    ENABLE_LLM: bool = os.getenv("ENABLE_LLM", "true").lower() == "true"
    ENABLE_LOGGING: bool = os.getenv("ENABLE_LOGGING", "true").lower() == "true"
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    @classmethod
    def has_llm_api_key(cls) -> bool:
        """Check if any LLM API key is available."""
        return bool(cls.OPENAI_API_KEY or cls.GEMINI_API_KEY)
    
    @classmethod
    def get_available_llm_provider(cls) -> Optional[str]:
        """Get the first available LLM provider."""
        if cls.OPENAI_API_KEY:
            return "openai"
        elif cls.GEMINI_API_KEY:
            return "gemini"
        return None

# Global configuration instance
config = Config()