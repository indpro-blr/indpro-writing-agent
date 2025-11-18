"""
AI Writing Assistant API Module

This module provides the core functionality for the AI Writing Assistant application,
including LangGraph workflows, prompt engineering, and content generation capabilities.

Main Functions:
    run_writing_agent: Execute the complete writing assistant workflow
    create_workflow: Build and compile the LangGraph state machine

Author: AI Writing Assistant Team
Version: 1.0.0
License: MIT
"""

from typing import Dict, Any, Optional
import logging

from .config import Config, get_config
from .utils import setup_logger

# Initialize logger first
logger = setup_logger(__name__)

# Try to import the full agent first, fallback to simple agent
try:
    from .agent import run_writing_agent, create_workflow
    LANGGRAPH_AVAILABLE = True
except ImportError:
    from .simple_agent import run_writing_agent_simple as run_writing_agent, health_check
    LANGGRAPH_AVAILABLE = False
    logger.warning("LangGraph not available, using simplified agent")

__version__ = "1.0.0"
__author__ = "AI Writing Assistant Team"

# Initialize module logger
logger = setup_logger(__name__)

# Export main functions based on available features
if LANGGRAPH_AVAILABLE:
    __all__ = [
        "run_writing_agent",
        "create_workflow", 
        "Config",
        "get_config",
        "setup_logger",
        "__version__",
        "__author__",
        "LANGGRAPH_AVAILABLE"
    ]
else:
    __all__ = [
        "run_writing_agent",
        "health_check",
        "Config",
        "get_config",
        "setup_logger",
        "__version__",
        "__author__",
        "LANGGRAPH_AVAILABLE"
    ]

def get_version() -> str:
    """
    Get the current version of the API module.
    
    Returns:
        str: Version string in semantic versioning format
    """
    return __version__

def health_check() -> Dict[str, Any]:
    """
    Perform a health check of the API module.
    
    Returns:
        Dict[str, Any]: Health status information
    """
    try:
        config = Config()
        return {
            "status": "healthy",
            "version": __version__,
            "config_loaded": True,
            "openai_configured": bool(config.OPENAI_API_KEY),
            "model": config.MODEL_NAME
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "version": __version__,
            "error": str(e)
        }

# Log module initialization
logger.info(f"AI Writing Assistant API module initialized - Version {__version__}")