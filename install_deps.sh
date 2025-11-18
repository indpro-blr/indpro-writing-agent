#!/bin/bash
# Quick installation script for AI Writing Assistant
# This script installs dependencies in the correct order to avoid conflicts

set -e  # Exit on any error

echo "🚀 Setting up AI Writing Assistant..."

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: No virtual environment detected."
    echo "   Run: source venv/bin/activate (or create with: python -m venv venv)"
    echo ""
fi

echo "📦 Installing dependencies in order..."

# Install core dependencies first (these are stable)
echo "1/4 Installing core Python dependencies..."
pip install --no-deps typing-extensions==4.8.0
pip install --no-deps python-dotenv==1.0.0
pip install --no-deps requests==2.31.0
pip install --no-deps httpx==0.25.2
pip install --no-deps numpy==1.24.4
pip install --no-deps jsonschema==4.17.3

# Install Pydantic (required by many packages)
echo "2/4 Installing Pydantic..."
pip install --no-deps pydantic-core==2.14.6
pip install --no-deps pydantic==2.5.3

# Install OpenAI and LangChain ecosystem
echo "3/4 Installing AI/ML dependencies..."
pip install --no-deps openai==1.3.9
pip install langchain==0.0.354
pip install langchain-openai==0.0.8
pip install langgraph==0.0.20

# Install Streamlit last
echo "4/4 Installing Streamlit..."
pip install streamlit==1.28.1

echo ""
echo "✅ Installation complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Copy environment file: cp .env.example .env"
echo "2. Add your OpenAI API key to .env"
echo "3. Run the app: streamlit run app.py"
echo ""
echo "🔧 If you encounter issues, try:"
echo "   pip install --upgrade pip"
echo "   pip install --force-reinstall -r requirements.txt"