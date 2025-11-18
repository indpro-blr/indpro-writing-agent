# Getting Started with AI Writing Assistant

This guide will walk you through setting up and running the AI Writing Assistant locally.

## Prerequisites

- **Python 3.10+** (Check with `python --version`)
- **OpenAI API Key** (Get one from [OpenAI Platform](https://platform.openai.com/api-keys))
- **Git** (for version control)

## Quick Start (5 minutes)

### 1. Clone and Navigate
```bash
git clone <your-repo-url>
cd english-writing-agent
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Verify activation (should show venv path)
which python
```

### 3. Install Dependencies
```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### 4. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API key
nano .env
# or
code .env
```

Add your OpenAI API key to `.env`:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 5. Run the Application
```bash
# Start Streamlit app
streamlit run app.py
```

Your app will open automatically at `http://localhost:8501`

## Detailed Setup Instructions

### Python Environment Setup

#### Option 1: Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Verify Python version
python --version  # Should be 3.10+
```

#### Option 2: Conda Environment
```bash
# Create conda environment
conda create -n writing-agent python=3.10

# Activate environment
conda activate writing-agent
```

### Dependencies Installation

#### Core Dependencies
```bash
# Essential packages for running the app
pip install -r requirements.txt
```

#### Development Dependencies (Optional)
```bash
# Testing, linting, and development tools
pip install -r requirements-dev.txt
```

#### Manual Installation (if requirements.txt fails)
```bash
pip install streamlit==1.29.0
pip install langgraph==0.0.26
pip install langchain
pip install openai
pip install python-dotenv
pip install typing-extensions
```

### Environment Configuration

#### 1. Create Environment File
```bash
cp .env.example .env
```

#### 2. Configure OpenAI API Key
Edit `.env` file:
```env
# Required: Your OpenAI API key
OPENAI_API_KEY=sk-your-actual-api-key-here

# Optional: Customize model settings
OPENAI_MODEL=gpt-4-turbo-preview
MAX_TOKENS=4096
TEMPERATURE=0.7

# Optional: Enable debug logging
LOG_LEVEL=INFO
```

#### 3. Streamlit Configuration (Optional)
The app includes pre-configured Streamlit settings in `.streamlit/config.toml`. You can customize:

```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[server]
port = 8501
headless = false
```

## Running the Application

### Local Development
```bash
# Activate your virtual environment first
source venv/bin/activate  # or conda activate writing-agent

# Start the application
streamlit run app.py

# App will be available at:
# Local URL: http://localhost:8501
# Network URL: http://192.168.x.x:8501
```

### Running with Custom Port
```bash
streamlit run app.py --server.port 8502
```

### Running in Production Mode
```bash
streamlit run app.py --server.headless true --server.port 8501
```

## Testing the Setup

### 1. Run Unit Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=api --cov-report=html

# Run specific test file
pytest tests/test_agent.py -v
```

### 2. Test the API Directly
```python
# Test in Python shell
python -c "
from api.agent import run_writing_agent
result = run_writing_agent(
    content_type='blog_post',
    topic='AI in healthcare',
    platform='linkedin'
)
print(result['content'])
"
```

### 3. Verify Streamlit App
1. Open `http://localhost:8501`
2. Adjust mood sliders
3. Select a platform (e.g., "LinkedIn")
4. Enter a topic (e.g., "The future of AI")
5. Click "Generate Content"

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Error: ModuleNotFoundError: No module named 'langgraph'
# Solution: Ensure virtual environment is activated and dependencies installed
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. OpenAI API Errors
```bash
# Error: openai.AuthenticationError
# Solution: Check your API key in .env file
cat .env | grep OPENAI_API_KEY
```

#### 3. Streamlit Port Issues
```bash
# Error: Port 8501 is already in use
# Solution: Use a different port
streamlit run app.py --server.port 8502
```

#### 4. Permission Errors (macOS/Linux)
```bash
# If you get permission errors
chmod +x venv/bin/activate
```

### Environment Verification Script
```bash
# Create a quick verification script
cat << 'EOF' > verify_setup.py
import sys
import os
from dotenv import load_dotenv

load_dotenv()

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current directory: {os.getcwd()}")
print(f"OpenAI API Key configured: {'OPENAI_API_KEY' in os.environ}")

try:
    import streamlit
    print(f"Streamlit version: {streamlit.__version__}")
except ImportError:
    print("❌ Streamlit not installed")

try:
    import langgraph
    print(f"LangGraph version: {langgraph.__version__}")
except ImportError:
    print("❌ LangGraph not installed")

try:
    import openai
    print(f"OpenAI version: {openai.__version__}")
except ImportError:
    print("❌ OpenAI not installed")

print("\n✅ Setup verification complete!")
EOF

python verify_setup.py
```

## Development Workflow

### 1. Daily Development
```bash
# Activate environment
source venv/bin/activate

# Start development server
streamlit run app.py

# In another terminal, run tests on file changes
pytest --watch
```

### 2. Code Quality Checks
```bash
# Format code
black .

# Lint code
flake8

# Type checking
mypy api/

# Run all quality checks
pre-commit run --all-files
```

### 3. Adding New Features
```bash
# Run tests before changes
pytest

# Make your changes
# ...

# Test your changes
pytest tests/test_your_feature.py

# Run full test suite
pytest --cov=api
```

## Next Steps

1. **Explore the UI**: Try different mood combinations and platforms
2. **Read the Documentation**: Check `docs/` folder for detailed guides
3. **Customize Prompts**: Modify `api/prompts.py` for your use case
4. **Deploy to Production**: Follow `docs/DEPLOYMENT.md` for Vercel deployment
5. **Extend Functionality**: Add new platforms or content types

## Getting Help

- **Documentation**: Check `docs/` folder for detailed guides
- **API Reference**: See `docs/API_REFERENCE.md`
- **Architecture**: Review `docs/ARCHITECTURE.md`
- **Issues**: Check logs in terminal for detailed error messages

## File Structure Quick Reference
```
english-writing-agent/
├── app.py                 # Main Streamlit application
├── api/                   # Core API logic
│   ├── agent.py          # LangGraph workflow
│   ├── prompts.py        # Prompt engineering
│   └── config.py         # Configuration management
├── tests/                # Test suite
├── docs/                 # Documentation
├── .env                  # Your environment variables
└── requirements.txt      # Dependencies
```

Ready to start writing with AI! 🚀