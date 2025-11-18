"""
Simplified AI Writing Agent for Vercel Deployment

A minimal version that uses OpenAI API directly without LangGraph 
to reduce bundle size for serverless deployment.
"""

import time
import logging
from typing import Dict, Any, Optional, List
from .config import get_config, ConfigurationError
from .prompts import (
    create_system_prompt, 
    create_user_prompt, 
    get_available_platforms,
    get_available_moods
)
from .utils import (
    count_words, 
    validate_word_count, 
    setup_logger, 
    create_request_id,
    estimate_tokens
)

logger = setup_logger(__name__)

def run_writing_agent_simple(
    description: str,
    mood_values: Dict[str, int],
    platform: str,
    max_retries: int = 2
) -> Dict[str, Any]:
    """
    Simplified writing agent using OpenAI API directly.
    
    Args:
        description: Content description from user
        mood_values: Dictionary of mood settings (0-10)
        platform: Target platform for content
        max_retries: Maximum retry attempts
        
    Returns:
        Dict containing success status, content, and metadata
    """
    start_time = time.time()
    request_id = create_request_id()
    
    try:
        # Import OpenAI here to handle missing dependency gracefully
        try:
            from openai import OpenAI
        except ImportError:
            logger.error("OpenAI library not available")
            return {
                "success": False,
                "error_message": "OpenAI library not available",
                "content": "",
                "request_id": request_id,
                "word_count": 0,
                "metadata": {}
            }
        
        # Get configuration
        config = get_config()
        
        if not config.OPENAI_API_KEY:
            logger.error("OpenAI API key not configured")
            return {
                "success": False,
                "error_message": "OpenAI API key not configured",
                "content": "",
                "request_id": request_id,
                "word_count": 0,
                "metadata": {}
            }
        
        # Validate inputs
        if not description or len(description.strip()) < 10:
            return {
                "success": False,
                "error_message": "Description must be at least 10 characters",
                "content": "",
                "request_id": request_id,
                "word_count": 0,
                "metadata": {}
            }
        
        if platform not in get_available_platforms():
            return {
                "success": False,
                "error_message": f"Invalid platform: {platform}",
                "content": "",
                "request_id": request_id,
                "word_count": 0,
                "metadata": {}
            }
        
        # Create prompts
        system_prompt = create_system_prompt(mood_values, platform)
        user_prompt = create_user_prompt(description, mood_values, platform)
        
        # Initialize OpenAI client
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        # Attempt generation with retries
        last_error = None
        total_retries = 0
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Generation attempt {attempt + 1} for request {request_id}")
                
                # Make API call
                response = client.chat.completions.create(
                    model=config.MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=config.MAX_TOKENS,
                    temperature=config.TEMPERATURE,
                    top_p=config.TOP_P,
                    timeout=config.TIMEOUT
                )
                
                # Extract content
                content = response.choices[0].message.content.strip()
                
                if not content:
                    raise ValueError("Empty response from OpenAI")
                
                # Validate content
                word_count = count_words(content)
                
                if not validate_word_count(word_count, platform):
                    logger.warning(f"Content length validation failed: {word_count} words for {platform}")
                
                # Success! Calculate timing
                processing_time = time.time() - start_time
                
                logger.info(f"Successfully generated content for request {request_id} in {processing_time:.2f}s")
                
                metadata = {
                    "request_id": request_id,
                    "model_name": config.MODEL_NAME,
                    "processing_time_seconds": processing_time,
                    "total_retries": total_retries,
                    "platform": platform,
                    "mood_summary": _create_mood_summary(mood_values),
                    "estimated_tokens": estimate_tokens(system_prompt + user_prompt + content),
                    "api_response_time": processing_time,
                    "timestamp": time.time()
                }
                
                return {
                    "success": True,
                    "content": content,
                    "request_id": request_id,
                    "word_count": word_count,
                    "metadata": metadata,
                    "error_message": None
                }
                
            except Exception as e:
                last_error = e
                total_retries = attempt
                
                logger.warning(f"Attempt {attempt + 1} failed for request {request_id}: {str(e)}")
                
                if attempt < max_retries:
                    # Wait before retry (exponential backoff)
                    wait_time = 2 ** attempt
                    logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                
        # All attempts failed
        processing_time = time.time() - start_time
        
        logger.error(f"All attempts failed for request {request_id}: {str(last_error)}")
        
        return {
            "success": False,
            "error_message": f"Generation failed after {max_retries + 1} attempts: {str(last_error)}",
            "content": "",
            "request_id": request_id,
            "word_count": 0,
            "metadata": {
                "request_id": request_id,
                "processing_time_seconds": processing_time,
                "total_retries": total_retries,
                "platform": platform,
                "timestamp": time.time(),
                "error": str(last_error)
            }
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Unexpected error in request {request_id}: {str(e)}")
        
        return {
            "success": False,
            "error_message": f"Unexpected error: {str(e)}",
            "content": "",
            "request_id": request_id,
            "word_count": 0,
            "metadata": {
                "request_id": request_id,
                "processing_time_seconds": processing_time,
                "total_retries": 0,
                "platform": platform,
                "timestamp": time.time(),
                "error": str(e)
            }
        }


def _create_mood_summary(mood_values: Dict[str, int]) -> str:
    """Create a summary of active moods."""
    active_moods = [(mood, value) for mood, value in mood_values.items() if value > 5]
    if not active_moods:
        return "Balanced tone"
    
    active_moods.sort(key=lambda x: x[1], reverse=True)
    top_moods = active_moods[:3]
    
    return ", ".join([f"{mood.title()} ({value})" for mood, value in top_moods])


def health_check() -> Dict[str, Any]:
    """
    Simple health check for the API.
    
    Returns:
        Dict with health status and basic info
    """
    try:
        config = get_config()
        
        return {
            "status": "healthy",
            "version": "1.0.0",
            "api_key_configured": bool(config.OPENAI_API_KEY),
            "model": config.MODEL_NAME,
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }