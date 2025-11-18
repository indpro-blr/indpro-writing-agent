<!-- Copilot Instructions for AI Writing Assistant Project -->

## Project Overview
This is an AI Writing Assistant application built with Python, LangGraph, and Streamlit, designed for deployment on Vercel. The project uses LangGraph for agent orchestration, OpenAI API for content generation, and provides a responsive Streamlit frontend.

## Architecture
- **Backend**: Python with LangGraph workflows in `api/` directory
- **Frontend**: Streamlit application in `app.py`
- **Testing**: Comprehensive test suite in `tests/` directory
- **Documentation**: Technical docs in `docs/` directory
- **Deployment**: Vercel serverless platform

## Development Guidelines
- Follow PEP 8 style guide with 100 character line limits
- Use type hints for all function signatures
- Include comprehensive docstrings with Args, Returns, Raises sections
- Implement proper error handling with specific exception types
- Use structured logging with timestamps and context
- Maintain minimum 70% code coverage for tests

## Key Components
- **LangGraph Workflow**: State machine in `api/agent.py`
- **Prompt Engineering**: Mood and platform-specific prompts in `api/prompts.py`
- **Configuration Management**: Environment variables in `api/config.py`
- **Streamlit UI**: Responsive interface with mood sliders and platform selection
- **Testing**: Unit tests, integration tests, and fixtures

## Code Quality Standards
- Black for code formatting
- Flake8 for linting
- MyPy for type checking
- Pre-commit hooks for automated quality checks
- Pytest for testing with proper mocking of external APIs

## Security Considerations
- No hardcoded API keys or secrets
- Input sanitization for all user inputs
- Environment variable validation
- Rate limiting for API calls
- Error logging without exposing sensitive information