"""
Configuration Management Module

This module handles all configuration settings for the AI Writing Assistant,
including environment variables, API settings, and application parameters.

Classes:
    Config: Main configuration class with validation and defaults
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass

class Config:
    """
    Configuration class for AI Writing Assistant.
    
    This class loads and validates all configuration settings from environment
    variables with sensible defaults and validation.
    
    Attributes:
        OPENAI_API_KEY (str): OpenAI API key for content generation
        MODEL_NAME (str): OpenAI model to use for generation
        MAX_TOKENS (int): Maximum tokens per generation request
        TEMPERATURE (float): Temperature setting for randomness
        TOP_P (float): Top-p setting for nucleus sampling
        MAX_RETRIES (int): Maximum retry attempts for API calls
        TIMEOUT (int): Request timeout in seconds
        LOG_LEVEL (str): Logging level for the application
    """
    
    def __init__(self):
        """Initialize configuration with environment variables and validation."""
        self._load_config()
        self._validate_config()
        self._setup_logging()
    
    def _load_config(self) -> None:
        """Load configuration from environment variables with defaults."""
        # OpenAI Configuration
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4-turbo-preview")
        
        # Generation Parameters
        self.MAX_TOKENS = int(os.getenv("MAX_TOKENS", "500"))
        self.TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
        self.TOP_P = float(os.getenv("TOP_P", "0.9"))
        
        # Retry and Timeout Settings
        self.MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))
        self.TIMEOUT = int(os.getenv("TIMEOUT", "30"))
        
        # Application Settings
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
        
        # Deployment Settings
        self.VERCEL_ENV = os.getenv("VERCEL_ENV", "development")
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        
        # Rate Limiting (tokens per minute)
        self.RATE_LIMIT_TPM = int(os.getenv("RATE_LIMIT_TPM", "40000"))
        
        # Application Limits
        self.MAX_DESCRIPTION_LENGTH = int(os.getenv("MAX_DESCRIPTION_LENGTH", "2000"))
        self.MIN_DESCRIPTION_LENGTH = int(os.getenv("MIN_DESCRIPTION_LENGTH", "10"))
    
    def _validate_config(self) -> None:
        """
        Validate configuration values and raise errors for invalid settings.
        
        Raises:
            ConfigurationError: If required configuration is missing or invalid
        """
        errors = []
        
        # Validate required fields
        if not self.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required but not provided")
        
        # Validate API key format (should start with sk-)
        if self.OPENAI_API_KEY and not self.OPENAI_API_KEY.startswith("sk-"):
            errors.append("OPENAI_API_KEY should start with 'sk-'")
        
        # Validate numeric ranges
        if not (0.0 <= self.TEMPERATURE <= 2.0):
            errors.append("TEMPERATURE must be between 0.0 and 2.0")
        
        if not (0.0 <= self.TOP_P <= 1.0):
            errors.append("TOP_P must be between 0.0 and 1.0")
        
        if self.MAX_TOKENS <= 0 or self.MAX_TOKENS > 4000:
            errors.append("MAX_TOKENS must be between 1 and 4000")
        
        if self.MAX_RETRIES < 0 or self.MAX_RETRIES > 5:
            errors.append("MAX_RETRIES must be between 0 and 5")
        
        if self.TIMEOUT <= 0 or self.TIMEOUT > 300:
            errors.append("TIMEOUT must be between 1 and 300 seconds")
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.LOG_LEVEL not in valid_log_levels:
            errors.append(f"LOG_LEVEL must be one of: {', '.join(valid_log_levels)}")
        
        # Validate description length limits
        if self.MIN_DESCRIPTION_LENGTH >= self.MAX_DESCRIPTION_LENGTH:
            errors.append("MIN_DESCRIPTION_LENGTH must be less than MAX_DESCRIPTION_LENGTH")
        
        if errors:
            error_message = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors)
            raise ConfigurationError(error_message)
    
    def _setup_logging(self) -> None:
        """Configure logging level based on configuration."""
        logging.getLogger().setLevel(getattr(logging, self.LOG_LEVEL))
    
    def get_openai_config(self) -> Dict[str, Any]:
        """
        Get OpenAI-specific configuration parameters.
        
        Returns:
            Dict[str, Any]: OpenAI configuration dictionary
        """
        return {
            "api_key": self.OPENAI_API_KEY,
            "model": self.MODEL_NAME,
            "max_tokens": self.MAX_TOKENS,
            "temperature": self.TEMPERATURE,
            "top_p": self.TOP_P,
            "timeout": self.TIMEOUT
        }
    
    def is_production(self) -> bool:
        """
        Check if running in production environment.
        
        Returns:
            bool: True if in production, False otherwise
        """
        return self.ENVIRONMENT.lower() == "production" or self.VERCEL_ENV == "production"
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current configuration (excluding sensitive data).
        
        Returns:
            Dict[str, Any]: Configuration summary
        """
        return {
            "model_name": self.MODEL_NAME,
            "max_tokens": self.MAX_TOKENS,
            "temperature": self.TEMPERATURE,
            "top_p": self.TOP_P,
            "max_retries": self.MAX_RETRIES,
            "timeout": self.TIMEOUT,
            "log_level": self.LOG_LEVEL,
            "environment": self.ENVIRONMENT,
            "api_key_configured": bool(self.OPENAI_API_KEY),
            "description_length_range": f"{self.MIN_DESCRIPTION_LENGTH}-{self.MAX_DESCRIPTION_LENGTH}"
        }

# Global configuration instance
_config: Optional[Config] = None

def get_config() -> Config:
    """
    Get the global configuration instance (singleton pattern).
    
    Returns:
        Config: Global configuration instance
    """
    global _config
    if _config is None:
        _config = Config()
    return _config

def reload_config() -> Config:
    """
    Reload configuration from environment variables.
    
    Returns:
        Config: New configuration instance
    """
    global _config
    load_dotenv(override=True)  # Reload .env file
    _config = Config()
    return _config