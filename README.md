# AI Writing Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-red.svg)](https://streamlit.io/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.0.26-green.svg)](https://github.com/langchain-ai/langgraph)

A sophisticated AI-powered writing assistant that generates customized content for various platforms using mood-based tone adjustment and OpenAI's GPT models. Built with Python, LangGraph, and Streamlit for seamless deployment on Vercel.

## ✨ Features

- **🎭 10-Dimensional Mood System**: Fine-tune content tone with professional, enthusiastic, empathetic, confident, creative, urgent, friendly, authoritative, humorous, and inspiring moods
- **🎯 Platform Optimization**: Optimized content generation for Twitter, LinkedIn, Instagram, Facebook, Blog, and Email
- **🔄 Advanced Workflow Engine**: Powered by LangGraph for reliable, traceable content generation with retry logic
- **🛡️ Anti-Hallucination Protection**: Multiple layers of validation to ensure high-quality, appropriate content
- **📱 Responsive Web Interface**: Modern Streamlit UI with mobile-friendly design
- **⚡ Real-time Generation**: Fast content creation with live word count and validation
- **📊 Generation Analytics**: Track performance metrics and content quality
- **🚀 One-Click Deployment**: Ready for deployment on Vercel with minimal configuration

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- OpenAI API key
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-writing-assistant.git
   cd ai-writing-assistant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser** to `http://localhost:8501`

## 🎯 Usage Examples

### Basic Content Generation

```python
from api import run_writing_agent

# Generate LinkedIn post about remote work
result = run_writing_agent(
    description="Write about the benefits of remote work for productivity",
    mood_values={
        'professional': 8,
        'confident': 7,
        'enthusiastic': 5,
        'empathetic': 4,
        'creative': 3,
        'urgent': 2,
        'friendly': 5,
        'authoritative': 6,
        'humorous': 2,
        'inspiring': 6
    },
    platform='linkedin'
)

if result['success']:
    print(f"Generated content: {result['content']}")
    print(f"Word count: {result['word_count']}")
else:
    print(f"Error: {result['error_message']}")
```

### Web Interface Usage

1. **Describe your content**: Enter a clear description of what you want to write about
2. **Customize mood**: Adjust the 10 mood sliders to set the desired tone
3. **Select platform**: Choose your target platform (Twitter, LinkedIn, etc.)
4. **Generate**: Click the generate button to create your content
5. **Refine**: Use the regenerate option or adjust moods for different variations

## 🏗️ Project Structure

```
ai-writing-assistant/
│
├── api/                          # Backend agent logic
│   ├── __init__.py              # API exports and health check
│   ├── agent.py                 # LangGraph workflow implementation  
│   ├── prompts.py               # Mood and platform prompt engineering
│   ├── config.py                # Configuration management
│   └── utils.py                 # Helper functions and utilities
│
├── tests/                        # Comprehensive test suite
│   ├── __init__.py              # Test configuration
│   ├── test_agent.py            # Agent workflow tests
│   ├── test_prompts.py          # Prompt generation tests
│   ├── test_integration.py      # End-to-end integration tests
│   └── fixtures/                # Test data and fixtures
│       └── sample_inputs.json
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md          # System architecture details
│   ├── API_REFERENCE.md         # Complete API documentation
│   ├── DEPLOYMENT.md            # Deployment guide
│   └── PROMPT_ENGINEERING.md    # Prompt design methodology
│
├── assets/                       # Static assets
│   └── styles.css               # Additional CSS styling
│
├── .streamlit/                   # Streamlit configuration
│   └── config.toml              # App settings and theme
│
├── app.py                        # Main Streamlit application
├── requirements.txt              # Python dependencies
├── requirements-dev.txt          # Development dependencies
├── vercel.json                   # Vercel deployment configuration
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore patterns
├── .pre-commit-config.yaml      # Code quality hooks
├── pytest.ini                    # Test configuration
└── README.md                     # This file
```

## 🎭 Mood System

The AI Writing Assistant features a sophisticated 10-dimensional mood system:

| Mood | Range | Description |
|------|-------|-------------|
| **Professional** | 0-10 | Controls formality and business appropriateness |
| **Enthusiastic** | 0-10 | Adjusts energy and excitement levels |
| **Empathetic** | 0-10 | Sets emotional understanding and care |
| **Confident** | 0-10 | Manages certainty and assertiveness |
| **Creative** | 0-10 | Controls originality and innovative language |
| **Urgent** | 0-10 | Adjusts time sensitivity and action orientation |
| **Friendly** | 0-10 | Sets warmth and approachability |
| **Authoritative** | 0-10 | Controls expertise demonstration |
| **Humorous** | 0-10 | Adjusts wit and lightness |
| **Inspiring** | 0-10 | Controls motivational and uplifting quality |

### Mood Presets

Choose from pre-configured mood combinations:

- **Professional Business**: High professional, confident, and authoritative
- **Friendly & Approachable**: Emphasizes friendly, empathetic, and enthusiastic
- **Creative & Inspiring**: Maximizes creative and inspiring with moderate enthusiasm
- **Urgent & Direct**: High urgency, confidence, and authority
- **Balanced & Neutral**: Moderate values across all dimensions

## 🎯 Platform Optimization

Content is automatically optimized for each platform:

### Twitter
- **Word Range**: 1-50 words
- **Style**: Conversational, engaging, hashtag-friendly
- **Focus**: Maximum impact in minimal space

### LinkedIn  
- **Word Range**: 10-300 words
- **Style**: Professional, networking-focused, thought leadership
- **Focus**: Industry insights and professional value

### Instagram
- **Word Range**: 5-150 words  
- **Style**: Visual-friendly, authentic, storytelling
- **Focus**: Lifestyle and personal connection

### Facebook
- **Word Range**: 5-200 words
- **Style**: Community-focused, personal sharing
- **Focus**: Social engagement and discussion

### Blog
- **Word Range**: 50-500 words
- **Style**: Informative, detailed, SEO-friendly
- **Focus**: Comprehensive value and readability

### Email
- **Word Range**: 20-400 words
- **Style**: Direct, purposeful, actionable
- **Focus**: Clear communication and results

## 🚀 Deployment

### Deploy to Vercel (Recommended)

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel
   ```

4. **Set Environment Variables**
   ```bash
   vercel env add OPENAI_API_KEY
   # Enter your OpenAI API key when prompted
   ```

### Alternative Deployments

- **Docker**: Use the included Dockerfile for containerized deployment
- **Heroku**: Compatible with Heroku's Python buildpack
- **Railway**: Simple deployment with GitHub integration
- **Local**: Run locally with `streamlit run app.py`

For detailed deployment instructions, see [DEPLOYMENT.md](docs/DEPLOYMENT.md).

## 🧪 Testing

The project includes comprehensive testing with 70%+ code coverage:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=api --cov-report=html

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m slow          # Slow/comprehensive tests
```

### Test Categories

- **Unit Tests**: Individual function and class testing
- **Integration Tests**: End-to-end workflow testing  
- **Mock Tests**: API interaction testing with mocked responses
- **Performance Tests**: Response time and resource usage testing

## 🛠️ Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run code formatting
black .

# Run linting
flake8 .

# Type checking
mypy api/
```

### Code Quality Standards

- **Black**: Code formatting with 100-character line limits
- **Flake8**: Linting and style checking
- **MyPy**: Static type checking
- **Pre-commit**: Automated quality checks
- **Pytest**: Comprehensive testing framework

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and quality checks
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Architecture Guide](docs/ARCHITECTURE.md)**: System design and component overview
- **[API Reference](docs/API_REFERENCE.md)**: Complete API documentation with examples
- **[Deployment Guide](docs/DEPLOYMENT.md)**: Detailed deployment instructions
- **[Prompt Engineering](docs/PROMPT_ENGINEERING.md)**: Mood system and prompt design

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | - | Yes |
| `MODEL_NAME` | OpenAI model | `gpt-4-turbo-preview` | No |
| `MAX_TOKENS` | Token limit per request | `500` | No |
| `TEMPERATURE` | Generation randomness | `0.7` | No |
| `TOP_P` | Nucleus sampling | `0.9` | No |
| `MAX_RETRIES` | API retry attempts | `2` | No |
| `TIMEOUT` | Request timeout (seconds) | `30` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

### Customization

The application supports extensive customization:

- **Custom Moods**: Add new mood dimensions in `api/prompts.py`
- **New Platforms**: Extend platform support with specifications
- **UI Themes**: Modify Streamlit theme in `.streamlit/config.toml`
- **API Providers**: Adapt for alternative LLM providers

## 📊 Performance

### Benchmarks

- **Generation Time**: < 3 seconds average
- **Memory Usage**: < 100MB typical
- **Concurrent Users**: Scales automatically on Vercel
- **API Efficiency**: Optimized token usage with retry logic

### Monitoring

Built-in monitoring includes:

- Request timing and performance metrics
- Error rate tracking and analysis
- API usage and token consumption
- User interaction analytics

## 🔒 Security

### Security Features

- **Input Sanitization**: Comprehensive XSS and injection protection
- **API Key Security**: Secure environment variable handling  
- **Rate Limiting**: Request throttling and abuse prevention
- **Content Validation**: Multi-layer quality and safety checks
- **No Data Persistence**: Stateless architecture protects privacy

### Best Practices

- Use environment variables for all secrets
- Regularly rotate API keys
- Monitor usage patterns for anomalies
- Keep dependencies updated
- Follow principle of least privilege

## 📈 Roadmap

### Version 1.1 (Planned)
- [ ] Multi-language support
- [ ] User account system with preferences
- [ ] Content templates and saved presets
- [ ] Advanced analytics dashboard
- [ ] API rate limiting improvements

### Version 1.2 (Future)
- [ ] Custom AI model fine-tuning
- [ ] Collaborative content creation
- [ ] Integration with social media APIs
- [ ] A/B testing for content optimization
- [ ] Voice input and audio output

### Long-term Vision
- [ ] Multi-modal content generation (text + images)
- [ ] Real-time collaboration features
- [ ] Enterprise team management
- [ ] Custom workflow automation
- [ ] Advanced AI training on user feedback

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

### Getting Help

- **Documentation**: Check the comprehensive docs in the `docs/` directory
- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Join conversations in GitHub Discussions
- **Email**: Contact the maintainers at [your-email@example.com]

### Common Issues

#### Import Errors
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.10+
```

#### API Key Issues
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test API connectivity
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

#### Deployment Issues
```bash
# Check Vercel configuration
vercel env ls

# View deployment logs
vercel logs
```

## 🙏 Acknowledgments

- **OpenAI** for providing the GPT models that power content generation
- **LangChain & LangGraph** for the excellent workflow orchestration framework
- **Streamlit** for the intuitive web application framework
- **Vercel** for seamless serverless deployment capabilities
- **The Open Source Community** for the amazing tools and libraries

## 📞 Contact

**Project Maintainer**: Your Name
- **Email**: your-email@example.com
- **GitHub**: [@yourusername](https://github.com/yourusername)
- **LinkedIn**: [Your LinkedIn Profile](https://linkedin.com/in/yourprofile)

**Project Link**: [https://github.com/yourusername/ai-writing-assistant](https://github.com/yourusername/ai-writing-assistant)

---

<div align="center">

**Made with ❤️ using Python, LangGraph, and Streamlit**

[⭐ Star this project](https://github.com/yourusername/ai-writing-assistant) | [🐛 Report Bug](https://github.com/yourusername/ai-writing-assistant/issues) | [💡 Request Feature](https://github.com/yourusername/ai-writing-assistant/issues)

</div>