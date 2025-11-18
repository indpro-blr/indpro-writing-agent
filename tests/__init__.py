"""
Test suite initialization for AI Writing Assistant.

This module provides common test utilities, fixtures, and configuration
for the entire test suite.
"""

import pytest
import os
import sys
from unittest.mock import Mock

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Test configuration
TEST_CONFIG = {
    "OPENAI_API_KEY": "sk-test-api-key-for-testing",
    "MODEL_NAME": "gpt-4-turbo-preview",
    "MAX_TOKENS": 500,
    "TEMPERATURE": 0.7,
    "LOG_LEVEL": "ERROR"  # Reduce noise during testing
}

def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    for key, value in TEST_CONFIG.items():
        os.environ[key] = str(value)
    
    yield
    
    # Cleanup
    for key in TEST_CONFIG.keys():
        os.environ.pop(key, None)