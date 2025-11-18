# AI Writing Assistant API Reference

## Overview

The AI Writing Assistant provides a programmatic interface for generating mood-customized content optimized for specific platforms. This document covers all available functions, classes, and configurations.

## Core API Functions

### `run_writing_agent(description, mood_values, platform, max_retries=2)`

Main entry point for content generation.

**Parameters:**
- `description` (str): Content topic or description (10-2000 characters)
- `mood_values` (Dict[str, int]): Mood intensity settings (0-10 scale)
- `platform` (str): Target platform (`'twitter'`, `'linkedin'`, `'instagram'`, `'facebook'`, `'blog'`, `'email'`)
- `max_retries` (int, optional): Maximum retry attempts (default: 2)

**Returns:**
- `Dict[str, Any]`: Generation results

**Return Structure:**
```python
{
    "success": bool,           # Generation success status
    "content": str,            # Generated content
    "word_count": int,         # Word count of content
    "platform_compliant": bool, # Platform requirements compliance
    "error_message": str,      # Error details (if any)
    "metadata": Dict[str, Any], # Processing metadata
    "request_id": str          # Unique request identifier
}
```

**Example Usage:**
```python
from api import run_writing_agent

result = run_writing_agent(
    description="Write about the benefits of remote work",
    mood_values={
        'professional': 8,
        'confident': 7,
        'enthusiastic': 4,
        'empathetic': 3,
        'creative': 4,
        'urgent': 2,
        'friendly': 5,
        'authoritative': 6,
        'humorous': 2,
        'inspiring': 5
    },
    platform='linkedin'
)

if result['success']:
    print(f"Generated content: {result['content']}")
    print(f"Word count: {result['word_count']}")
else:
    print(f"Error: {result['error_message']}")
```

### `create_workflow()`

Creates and compiles the LangGraph workflow.

**Returns:**
- `CompiledGraph`: Compiled LangGraph workflow instance

**Usage:**
```python
from api.agent import create_workflow

workflow = create_workflow()
# Use workflow.invoke(state) for custom execution
```

## Configuration Classes

### `Config`

Main configuration class for application settings.

**Attributes:**
- `OPENAI_API_KEY` (str): OpenAI API key
- `MODEL_NAME` (str): OpenAI model name (default: "gpt-4-turbo-preview")
- `MAX_TOKENS` (int): Maximum tokens per request (default: 500)
- `TEMPERATURE` (float): Generation temperature (default: 0.7)
- `TOP_P` (float): Top-p sampling parameter (default: 0.9)
- `MAX_RETRIES` (int): Maximum retry attempts (default: 2)
- `TIMEOUT` (int): Request timeout in seconds (default: 30)
- `LOG_LEVEL` (str): Logging level (default: "INFO")

**Methods:**

#### `get_openai_config()`
Returns OpenAI-specific configuration parameters.

**Returns:**
- `Dict[str, Any]`: OpenAI configuration

#### `is_production()`
Checks if running in production environment.

**Returns:**
- `bool`: True if production environment

#### `get_summary()`
Returns configuration summary (excluding sensitive data).

**Returns:**
- `Dict[str, Any]`: Configuration summary

**Usage:**
```python
from api.config import Config

config = Config()
print(f"Model: {config.MODEL_NAME}")
print(f"Max tokens: {config.MAX_TOKENS}")

# Get OpenAI config
openai_config = config.get_openai_config()
```

## Prompt Engineering Functions

### `get_mood_instruction(mood_name, intensity)`

Generate mood-specific instruction text.

**Parameters:**
- `mood_name` (str): Mood name (see Available Moods)
- `intensity` (int): Intensity level (0-10)

**Returns:**
- `str`: Detailed mood instruction

**Raises:**
- `ValueError`: If mood_name is invalid or intensity out of range

### `build_mood_combination_prompt(mood_values)`

Combine multiple mood instructions into cohesive prompt.

**Parameters:**
- `mood_values` (Dict[str, int]): Mood intensity settings

**Returns:**
- `str`: Combined mood instruction prompt

### `build_anti_hallucination_prompt(description, mood_values, platform)`

Create comprehensive system prompt with anti-hallucination strategies.

**Parameters:**
- `description` (str): Content description
- `mood_values` (Dict[str, int]): Mood settings
- `platform` (str): Target platform

**Returns:**
- `str`: Complete system prompt

**Raises:**
- `ValueError`: If parameters are invalid

### `get_platform_word_limit(platform)`

Get word count limits for specific platform.

**Parameters:**
- `platform` (str): Platform name

**Returns:**
- `Dict[str, int]`: Dictionary with 'min' and 'max' limits

### `get_available_moods()`

Get list of all available mood types.

**Returns:**
- `List[str]`: List of mood names

### `get_available_platforms()`

Get list of all available platforms.

**Returns:**
- `List[str]`: List of platform names

### `create_mood_summary(mood_values)`

Create human-readable summary of active moods.

**Parameters:**
- `mood_values` (Dict[str, int]): Mood settings

**Returns:**
- `str`: Summary of active moods

### `validate_mood_combination(mood_values)`

Validate mood combination and return warnings.

**Parameters:**
- `mood_values` (Dict[str, int]): Mood settings

**Returns:**
- `List[str]`: List of validation warnings

## Utility Functions

### `count_words(text)`

Count words in given text.

**Parameters:**
- `text` (str): Text to count

**Returns:**
- `int`: Word count

### `validate_word_count(text, platform)`

Validate text meets platform word count requirements.

**Parameters:**
- `text` (str): Text to validate
- `platform` (str): Target platform

**Returns:**
- `bool`: True if within platform limits

### `detect_hallucination_markers(text)`

Detect potential hallucination markers in text.

**Parameters:**
- `text` (str): Text to analyze

**Returns:**
- `List[str]`: List of detected patterns

### `sanitize_input(text)`

Clean and sanitize user input text.

**Parameters:**
- `text` (str): Raw input text

**Returns:**
- `str`: Sanitized text

### `setup_logger(name, level="INFO")`

Set up structured logging for a module.

**Parameters:**
- `name` (str): Logger name
- `level` (str): Logging level

**Returns:**
- `logging.Logger`: Configured logger

### `estimate_tokens(text, model="gpt-4")`

Estimate token count for text.

**Parameters:**
- `text` (str): Text to estimate
- `model` (str): Model name for estimation

**Returns:**
- `int`: Estimated token count

## Data Structures

### `AgentState` (TypedDict)

State structure for LangGraph workflow.

```python
class AgentState(TypedDict):
    # Input parameters
    description: str
    mood_values: Dict[str, int]
    platform: str
    
    # Generated content and processing
    system_prompt: str
    generated_content: str
    validation_passed: bool
    
    # Error handling and retry logic
    retry_count: int
    max_retries: int
    error_message: str
    
    # Metadata and tracking
    metadata: Dict[str, Any]
    request_id: str
    start_time: float
    
    # Quality metrics
    word_count: int
    hallucination_markers: List[str]
    platform_compliant: bool
```

## Available Moods

The system supports 10 mood dimensions, each with 0-10 intensity scale:

1. **Professional**: Formality and business appropriateness
2. **Enthusiastic**: Energy and excitement level
3. **Empathetic**: Emotional understanding and care
4. **Confident**: Certainty and assertiveness
5. **Creative**: Originality and innovation
6. **Urgent**: Time sensitivity and action orientation
7. **Friendly**: Warmth and approachability
8. **Authoritative**: Expertise and leadership demonstration
9. **Humorous**: Wit and lightness
10. **Inspiring**: Motivational and uplifting quality

## Supported Platforms

### Twitter
- **Word Range**: 1-50 words
- **Character Limit**: 280 characters
- **Tone**: Conversational and engaging
- **Features**: Hashtags, brevity, viral potential

### LinkedIn
- **Word Range**: 10-300 words
- **Character Limit**: 3000 characters
- **Tone**: Professional and networking-focused
- **Features**: Thought leadership, industry insights

### Instagram
- **Word Range**: 5-150 words
- **Character Limit**: 2200 characters
- **Tone**: Visual and lifestyle-oriented
- **Features**: Hashtags, storytelling, authenticity

### Facebook
- **Word Range**: 5-200 words
- **Character Limit**: 63206 characters
- **Tone**: Personal and community-focused
- **Features**: Community engagement, personal sharing

### Blog
- **Word Range**: 50-500 words
- **Character Limit**: None
- **Tone**: Informative and engaging
- **Features**: Detailed content, SEO considerations

### Email
- **Word Range**: 20-400 words
- **Character Limit**: None
- **Tone**: Direct and purposeful
- **Features**: Clear subject, actionable content

## Error Handling

### Exception Types

#### `ConfigurationError`
Raised when configuration is invalid or missing.

```python
from api.config import ConfigurationError

try:
    config = Config()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

### Error Response Format

When `run_writing_agent` fails, it returns:

```python
{
    "success": False,
    "content": "",
    "word_count": 0,
    "platform_compliant": False,
    "error_message": "Detailed error description",
    "metadata": {"request_id": "req_...", "execution_time": 1.23},
    "request_id": "req_..."
}
```

### Common Error Messages

- `"Description cannot be empty"`: Empty or whitespace-only description
- `"Description must be at least 10 characters long"`: Description too short
- `"Description must be less than 2000 characters"`: Description too long
- `"Invalid platform: {platform}"`: Unsupported platform specified
- `"Mood value for '{mood}' must be integer between 0-10"`: Invalid mood value
- `"OpenAI API key not configured"`: Missing API key
- `"Generated content is empty"`: API returned empty response

## Environment Variables

Required environment variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
MODEL_NAME=gpt-4-turbo-preview
MAX_TOKENS=500
TEMPERATURE=0.7
TOP_P=0.9

# Application Settings
LOG_LEVEL=INFO
MAX_RETRIES=2
TIMEOUT=30
ENVIRONMENT=development
```

## Rate Limits and Quotas

### OpenAI API Limits
- **Tokens per minute**: 40,000 (configurable via `RATE_LIMIT_TPM`)
- **Requests per minute**: Varies by model and tier
- **Request timeout**: 30 seconds (configurable)

### Application Limits
- **Description length**: 10-2000 characters
- **Max retries**: 0-5 attempts
- **Concurrent requests**: Limited by deployment platform

## Best Practices

### 1. Input Validation
Always validate inputs before calling the API:

```python
def validate_inputs(description, mood_values, platform):
    if not description or len(description.strip()) < 10:
        raise ValueError("Description too short")
    
    if platform not in get_available_platforms():
        raise ValueError(f"Invalid platform: {platform}")
    
    for mood, value in mood_values.items():
        if not isinstance(value, int) or not (0 <= value <= 10):
            raise ValueError(f"Invalid mood value: {mood}={value}")
```

### 2. Error Handling
Implement comprehensive error handling:

```python
try:
    result = run_writing_agent(description, mood_values, platform)
    
    if result['success']:
        return result['content']
    else:
        # Handle specific error types
        if 'api key' in result['error_message'].lower():
            # Handle API key issues
            pass
        elif 'rate limit' in result['error_message'].lower():
            # Handle rate limiting
            pass
        else:
            # Handle other errors
            pass
            
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected error: {e}")
```

### 3. Configuration Management
Use proper configuration management:

```python
from api.config import get_config

config = get_config()

if not config.is_production():
    # Development-specific settings
    config.LOG_LEVEL = "DEBUG"
```

### 4. Async Usage
For high-throughput applications:

```python
import asyncio
from api.agent import run_writing_agent_async

async def generate_multiple_contents(requests):
    tasks = [
        run_writing_agent_async(req['description'], req['mood_values'], req['platform'])
        for req in requests
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

## Testing

### Unit Testing
```python
import pytest
from api import run_writing_agent

@pytest.mark.unit
def test_content_generation():
    result = run_writing_agent(
        "Test description",
        {'professional': 5},
        'twitter'
    )
    
    assert result['success'] is True
    assert result['content'] != ''
```

### Integration Testing
```python
@pytest.mark.integration
def test_full_workflow():
    # Test complete workflow with real API calls
    pass
```

## Migration Guide

### From v0.9 to v1.0
- Update import statements: `from api import run_writing_agent`
- Replace deprecated `generate_content()` with `run_writing_agent()`
- Update mood value format from strings to integers
- Add error handling for new response format

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **API Key Issues**: Verify `OPENAI_API_KEY` environment variable
3. **Rate Limiting**: Implement exponential backoff
4. **Memory Issues**: Monitor token usage and request frequency
5. **Timeout Errors**: Increase `TIMEOUT` configuration value

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or via environment variable
# LOG_LEVEL=DEBUG
```