# Deployment Guide

## Overview

This guide covers deploying the AI Writing Assistant to various platforms, with primary focus on Vercel serverless deployment. The application is designed for easy deployment with minimal configuration.

## Prerequisites

- Node.js 18+ (for Vercel CLI)
- Python 3.10+
- OpenAI API key
- Git repository

## Quick Start Deployment

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd ai-writing-assistant
cp .env.example .env
# Edit .env with your OpenAI API key
```

### 2. Install Vercel CLI

```bash
npm install -g vercel
```

### 3. Deploy to Vercel

```bash
vercel login
vercel
```

Follow the prompts to deploy your application.

## Detailed Deployment Instructions

### Vercel Deployment

Vercel is the recommended platform for deploying the AI Writing Assistant due to its excellent Python support and serverless architecture.

#### Step 1: Prepare Your Repository

Ensure your repository contains:
- `app.py` (main Streamlit application)
- `requirements.txt` (Python dependencies)
- `vercel.json` (Vercel configuration)
- `api/` directory (core application logic)

#### Step 2: Configure Environment Variables

In your Vercel dashboard or via CLI:

```bash
vercel env add OPENAI_API_KEY
# Enter your OpenAI API key when prompted

vercel env add MODEL_NAME
# Enter: gpt-4-turbo-preview

vercel env add MAX_TOKENS
# Enter: 500

vercel env add TEMPERATURE  
# Enter: 0.7

vercel env add LOG_LEVEL
# Enter: INFO

vercel env add ENVIRONMENT
# Enter: production
```

#### Step 3: Deploy

```bash
# For first deployment
vercel

# For subsequent deployments
vercel --prod
```

#### Step 4: Verify Deployment

Visit your Vercel URL to confirm the application is running correctly.

### Alternative Deployment Platforms

#### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:

```bash
docker build -t ai-writing-assistant .
docker run -p 8501:8501 --env-file .env ai-writing-assistant
```

#### Heroku Deployment

1. Create `Procfile`:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

2. Deploy:
```bash
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your-key-here
git push heroku main
```

#### Railway Deployment

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on git push

## Configuration Management

### Environment Variables

#### Required Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` | Yes |
| `MODEL_NAME` | OpenAI model | `gpt-4-turbo-preview` | No |
| `MAX_TOKENS` | Token limit | `500` | No |
| `TEMPERATURE` | Generation temperature | `0.7` | No |
| `TOP_P` | Top-p sampling | `0.9` | No |
| `MAX_RETRIES` | Retry attempts | `2` | No |
| `TIMEOUT` | Request timeout | `30` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `ENVIRONMENT` | Environment type | `production` | No |

#### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MAX_DESCRIPTION_LENGTH` | Max input length | `2000` |
| `MIN_DESCRIPTION_LENGTH` | Min input length | `10` |
| `RATE_LIMIT_TPM` | Tokens per minute | `40000` |

### Platform-Specific Configuration

#### Vercel Configuration (`vercel.json`)

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb",
        "runtime": "python3.10"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "functions": {
    "app.py": {
      "maxDuration": 30
    }
  }
}
```

#### Streamlit Configuration (`.streamlit/config.toml`)

```toml
[server]
port = 8501
headless = true
enableCORS = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#4CAF50"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

## Monitoring and Logging

### Application Monitoring

#### Vercel Analytics

Enable analytics in your Vercel dashboard:
1. Go to your project settings
2. Enable "Analytics"
3. Monitor traffic, performance, and errors

#### Custom Logging

The application includes structured logging:

```python
# Enable debug logging
LOG_LEVEL=DEBUG

# View logs in Vercel
vercel logs
```

### Error Tracking

#### Sentry Integration (Optional)

Add Sentry for error tracking:

```bash
pip install sentry-sdk
```

```python
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[LoggingIntegration()],
    traces_sample_rate=1.0,
)
```

#### Health Check Endpoint

The application includes a health check:

```python
from api import health_check

status = health_check()
print(status)  # {"status": "healthy", "version": "1.0.0", ...}
```

## Performance Optimization

### Caching Strategies

#### Response Caching

Implement caching for repeated requests:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_generation(description_hash, mood_hash, platform):
    # Cache based on content hash
    pass
```

#### CDN Configuration

For static assets, configure CDN:

```json
{
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

### Resource Optimization

#### Memory Management

Monitor memory usage:

```python
import psutil
import os

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB
```

#### Request Optimization

Optimize API requests:

```python
# Use connection pooling
import httpx

client = httpx.Client(
    timeout=30.0,
    limits=httpx.Limits(max_connections=10)
)
```

## Security Considerations

### API Key Security

#### Environment Variables Only
Never hardcode API keys:

```python
# ❌ Wrong
api_key = "sk-1234567890"

# ✅ Correct  
api_key = os.getenv("OPENAI_API_KEY")
```

#### Key Rotation
Regularly rotate your OpenAI API keys:

1. Generate new key in OpenAI dashboard
2. Update environment variable
3. Redeploy application
4. Delete old key

### Input Validation

The application includes comprehensive input validation:

```python
def validate_input(description, mood_values, platform):
    # Length validation
    if len(description) > 2000:
        raise ValueError("Description too long")
    
    # XSS prevention
    description = sanitize_input(description)
    
    # Platform validation
    if platform not in ALLOWED_PLATFORMS:
        raise ValueError("Invalid platform")
```

### Rate Limiting

Implement rate limiting:

```python
from functools import wraps
import time

def rate_limit(calls_per_minute=60):
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = 60.0 / calls_per_minute - elapsed
            
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        
        return wrapper
    return decorator
```

## Scaling Considerations

### Horizontal Scaling

Vercel automatically handles horizontal scaling, but consider:

1. **Stateless Design**: Ensure no server-side state
2. **Database Connections**: Use connection pooling
3. **Cache Distribution**: Use distributed caching

### Performance Monitoring

Monitor key metrics:

```python
import time
import logging

def performance_monitor(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logging.info(f"{func.__name__} took {end_time - start_time:.2f}s")
        return result
    
    return wrapper
```

## Troubleshooting Deployment Issues

### Common Issues

#### 1. Build Failures

```bash
# Check Python version
python --version

# Verify requirements.txt
pip install -r requirements.txt

# Check for syntax errors
python -m py_compile app.py
```

#### 2. Runtime Errors

```bash
# Check environment variables
vercel env ls

# View application logs
vercel logs

# Test locally
streamlit run app.py
```

#### 3. API Connection Issues

```bash
# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# Check network connectivity
ping api.openai.com
```

#### 4. Performance Issues

Monitor and optimize:

```python
# Add timing to functions
import time

start = time.time()
result = slow_function()
print(f"Function took {time.time() - start:.2f}s")
```

### Debug Mode

Enable comprehensive debugging:

```bash
# Set environment variables
LOG_LEVEL=DEBUG
STREAMLIT_LOGGER_LEVEL=debug

# Run with debug output
streamlit run app.py --logger.level=debug
```

### Health Checks

Implement health checks:

```python
def health_check():
    checks = {
        "api_key": bool(os.getenv("OPENAI_API_KEY")),
        "dependencies": True,  # Check imports
        "connectivity": True   # Check API access
    }
    
    return {
        "healthy": all(checks.values()),
        "checks": checks,
        "timestamp": time.time()
    }
```

## Rollback Procedures

### Vercel Rollback

```bash
# List deployments
vercel ls

# Rollback to previous deployment
vercel rollback [deployment-url]
```

### Manual Rollback

1. Keep previous version tagged in git
2. Redeploy from previous commit
3. Update environment variables if needed

### Emergency Procedures

1. **Immediate Issues**: Use Vercel dashboard to rollback
2. **API Issues**: Switch to backup API key
3. **Critical Bugs**: Deploy hotfix or rollback
4. **Performance Issues**: Scale down features temporarily

## Continuous Deployment

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Vercel

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install Vercel CLI
        run: npm install --global vercel@latest
        
      - name: Pull Vercel Environment
        run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}
        
      - name: Build Project
        run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}
        
      - name: Deploy to Vercel
        run: vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
```

### Automated Testing

Include testing in deployment pipeline:

```yaml
- name: Run Tests
  run: |
    pip install -r requirements-dev.txt
    pytest tests/ --cov=api
```

## Cost Optimization

### OpenAI API Costs

Monitor and optimize:

1. **Token Usage**: Track and limit tokens per request
2. **Model Selection**: Use appropriate models for tasks
3. **Caching**: Cache repeated requests
4. **Rate Limiting**: Prevent excessive usage

### Vercel Costs

Optimize function usage:

1. **Cold Starts**: Minimize by keeping functions warm
2. **Execution Time**: Optimize code for faster execution
3. **Memory Usage**: Monitor and optimize memory consumption
4. **Bandwidth**: Optimize response sizes

## Backup and Recovery

### Configuration Backup

```bash
# Export environment variables
vercel env pull .env.production

# Backup configuration
git add vercel.json .streamlit/config.toml
git commit -m "Backup configuration"
```

### Data Recovery

Since the application is stateless:

1. Configuration recovery from git
2. Environment variables from Vercel dashboard
3. API keys from OpenAI dashboard

### Disaster Recovery Plan

1. **Service Outage**: Deploy to alternative platform
2. **API Issues**: Switch to backup API provider
3. **Code Issues**: Rollback to last known good version
4. **Configuration Loss**: Restore from git and environment backups