"""
Utility Functions Module

This module provides helper functions for the AI Writing Assistant,
including text processing, validation, logging setup, and token estimation.

Functions:
    count_words: Count words in text
    validate_word_count: Validate text length for specific platforms
    detect_hallucination_markers: Detect potential hallucination patterns
    sanitize_input: Clean and sanitize user input
    setup_logger: Configure structured logging
    estimate_tokens: Estimate token count for text
"""

import re
import logging
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime
import unicodedata

# Platform-specific word count ranges
PLATFORM_WORD_LIMITS = {
    "twitter": {"min": 1, "max": 50},
    "linkedin": {"min": 10, "max": 300},
    "instagram": {"min": 5, "max": 150},
    "facebook": {"min": 5, "max": 200},
    "blog": {"min": 50, "max": 500},
    "email": {"min": 20, "max": 400}
}

# Common hallucination markers to detect
HALLUCINATION_MARKERS = [
    r"as an ai",
    r"i (don't|can't|cannot) (have|access|provide)",
    r"i (am|am not) (able to|capable of)",
    r"as a language model",
    r"i don't have access to",
    r"i cannot (browse|access|see)",
    r"as of my (last update|knowledge cutoff)",
    r"i (don't|can't) browse the internet",
    r"i (am|was) trained",
    r"my training data",
    r"here (is|are) some",
    r"let me (help|assist) you",
    r"i'd be happy to",
    r"feel free to",
    r"please let me know"
]

def count_words(text: str) -> int:
    """
    Count words in the given text.
    
    Args:
        text (str): Text to count words in
        
    Returns:
        int: Number of words in the text
    """
    if not text or not isinstance(text, str):
        return 0
    
    # Remove extra whitespace and split by whitespace
    words = text.strip().split()
    
    # Filter out empty strings and count actual words
    return len([word for word in words if word.strip()])

def validate_word_count(text: str, platform: str) -> bool:
    """
    Validate if text meets word count requirements for specified platform.
    
    Args:
        text (str): Text to validate
        platform (str): Target platform (twitter, linkedin, etc.)
        
    Returns:
        bool: True if word count is within platform limits
    """
    if not text or not platform:
        return False
    
    platform = platform.lower()
    if platform not in PLATFORM_WORD_LIMITS:
        # If platform not recognized, use general limits
        word_count = count_words(text)
        return 1 <= word_count <= 500
    
    limits = PLATFORM_WORD_LIMITS[platform]
    word_count = count_words(text)
    
    return limits["min"] <= word_count <= limits["max"]

def detect_hallucination_markers(text: str) -> List[str]:
    """
    Detect potential hallucination markers in generated text.
    
    Args:
        text (str): Text to analyze for hallucination markers
        
    Returns:
        List[str]: List of detected hallucination patterns
    """
    if not text or not isinstance(text, str):
        return []
    
    text_lower = text.lower()
    detected_markers = []
    
    for marker_pattern in HALLUCINATION_MARKERS:
        if re.search(marker_pattern, text_lower, re.IGNORECASE):
            detected_markers.append(marker_pattern)
    
    return detected_markers

def sanitize_input(text: str) -> str:
    """
    Clean and sanitize user input text.
    
    Args:
        text (str): Raw input text to sanitize
        
    Returns:
        str: Sanitized text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKC', text)
    
    # Remove or replace potentially harmful characters
    # Remove control characters except newlines and tabs
    text = ''.join(char for char in text if not unicodedata.category(char).startswith('C') 
                   or char in '\n\t\r')
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove potentially malicious patterns
    # Remove HTML/XML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove script injections
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    
    # Limit length to prevent abuse
    max_length = 2000
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Set up structured logging for a module.
    
    Args:
        name (str): Logger name (usually __name__)
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Don't add handlers if they already exist
    if logger.handlers:
        return logger
    
    # Set level
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create and configure handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger

def estimate_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Estimate token count for given text (rough approximation).
    
    This is a simplified estimation. For accurate token counting,
    use tiktoken library with the specific model's tokenizer.
    
    Args:
        text (str): Text to estimate tokens for
        model (str): Model name (affects token estimation)
        
    Returns:
        int: Estimated token count
    """
    if not text or not isinstance(text, str):
        return 0
    
    # Rough estimation: 1 token ≈ 4 characters for English text
    # GPT-4 generally uses more tokens than GPT-3.5
    if "gpt-4" in model.lower():
        # GPT-4 tends to use slightly more tokens
        char_per_token = 3.5
    else:
        char_per_token = 4.0
    
    # Count characters (excluding whitespace for better estimation)
    char_count = len(text.replace(' ', ''))
    
    # Estimate tokens
    estimated_tokens = int(char_count / char_per_token)
    
    # Add buffer for special tokens and formatting
    buffer = max(10, int(estimated_tokens * 0.1))
    
    return estimated_tokens + buffer

def get_platform_limits(platform: str) -> Optional[Dict[str, int]]:
    """
    Get word count limits for a specific platform.
    
    Args:
        platform (str): Platform name
        
    Returns:
        Optional[Dict[str, int]]: Platform limits or None if not found
    """
    return PLATFORM_WORD_LIMITS.get(platform.lower())

def validate_mood_values(mood_values: Dict[str, int]) -> bool:
    """
    Validate mood values are within acceptable ranges.
    
    Args:
        mood_values (Dict[str, int]): Dictionary of mood names to intensity values
        
    Returns:
        bool: True if all mood values are valid (0-10 range)
    """
    if not isinstance(mood_values, dict):
        return False
    
    for mood, value in mood_values.items():
        if not isinstance(value, int) or not (0 <= value <= 10):
            return False
    
    return True

def format_error_message(error: Exception, context: str = "") -> str:
    """
    Format error message for user-friendly display.
    
    Args:
        error (Exception): Exception to format
        context (str): Additional context about where error occurred
        
    Returns:
        str: Formatted error message
    """
    error_type = type(error).__name__
    error_message = str(error)
    
    if context:
        return f"{context}: {error_type} - {error_message}"
    else:
        return f"{error_type}: {error_message}"

def create_request_id() -> str:
    """
    Generate a unique request ID for tracking.
    
    Returns:
        str: Unique request identifier
    """
    import uuid
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"req_{timestamp}_{unique_id}"