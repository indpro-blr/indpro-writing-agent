# Deploying to Streamlit.io

This guide will walk you through deploying your AI Writing Assistant to Streamlit.io.

## Prerequisites

1. **GitHub Repository**: Your code should be in a public GitHub repository (✅ Done)
   - Repository: `https://github.com/indpro-blr/indpro-writing-agent.git`

2. **OpenAI API Key**: You'll need an API key from OpenAI
   - Get it from: https://platform.openai.com/api-keys
   - Keep it secure - never commit it to your repository

## Step-by-Step Deployment

### 1. Prepare Your Repository

Your repository is already prepared with the necessary files:
- ✅ `app.py` - Main Streamlit application
- ✅ `requirements.txt` - Python dependencies
- ✅ `packages.txt` - System dependencies (if needed)
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `.streamlit/secrets.toml.template` - Secrets template

### 2. Create a Streamlit.io Account

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Grant Streamlit access to your GitHub repositories

### 3. Deploy Your App

1. **Click "New app"** on the Streamlit.io dashboard

2. **Configure your app:**
   - **Repository**: `indpro-blr/indpro-writing-agent`
   - **Branch**: `main` (or your default branch)
   - **Main file path**: `app.py`
   - **App URL**: Choose a custom URL (e.g., `indpro-writing-agent`)

3. **Click "Deploy!"**

### 4. Configure Secrets (IMPORTANT!)

After deployment, you need to configure your OpenAI API key:

1. **Go to your app settings:**
   - Click on your app in the Streamlit.io dashboard
   - Click the "⚙️" (settings) icon
   - Click "Secrets" in the left sidebar

2. **Add your secrets:**
   ```toml
   # Paste this into the secrets editor and replace with your actual values
   
   [general]
   OPENAI_API_KEY = "sk-your-actual-openai-api-key-here"
   
   # Optional - customize these if needed
   MODEL_NAME = "gpt-4-turbo-preview"
   MAX_TOKENS = "500"
   TEMPERATURE = "0.7"
   TOP_P = "0.9"
   MAX_RETRIES = "2"
   TIMEOUT = "30"
   LOG_LEVEL = "INFO"
   ENVIRONMENT = "production"
   ```

3. **Click "Save"**

4. **Reboot your app:**
   - Click "Reboot" to restart with the new secrets

### 5. Test Your Deployment

1. Visit your app URL (e.g., `https://indpro-writing-agent.streamlit.app`)
2. Try generating content to ensure everything works
3. Check that the API integration is functioning

## Troubleshooting

### Common Issues

1. **"ModuleNotFoundError"**
   - Check that all dependencies are listed in `requirements.txt`
   - Ensure the versions are compatible with Streamlit.io

2. **"API Key not found"**
   - Verify your `OPENAI_API_KEY` is correctly set in Secrets
   - Make sure there are no extra spaces or characters
   - Ensure the key starts with `sk-`

3. **"Import errors"**
   - The app is designed to handle import errors gracefully
   - Check the logs in Streamlit.io for specific error messages

4. **"Timeout errors"**
   - Increase the `TIMEOUT` value in secrets
   - Check your OpenAI API usage and rate limits

### App Logs

To view logs:
1. Go to your app on Streamlit.io
2. Click "Manage app"
3. View the logs in the bottom panel

### Updating Your App

When you push changes to GitHub:
1. Streamlit.io will automatically detect changes
2. The app will redeploy automatically
3. No manual action required

## App Features

Your deployed app includes:

- **Interactive Mood Sliders**: Customize content tone
- **Platform Selection**: Optimize for different social platforms
- **Real-time Generation**: Powered by OpenAI GPT-4
- **Copy Functionality**: One-click content copying
- **Generation History**: Track your content creation
- **Responsive Design**: Works on desktop and mobile

## Security Notes

- ✅ API keys are stored securely in Streamlit secrets
- ✅ No sensitive data is committed to the repository
- ✅ Environment variables are properly configured
- ✅ Rate limiting is implemented to prevent abuse

## Support

If you encounter issues:

1. **Check the logs** in your Streamlit.io app dashboard
2. **Verify secrets** are correctly configured
3. **Test locally** using the same configuration
4. **Review the error messages** for specific guidance

## Next Steps

After successful deployment:

1. **Share your app** with users
2. **Monitor usage** through Streamlit.io analytics
3. **Update content** by pushing to GitHub
4. **Scale up** OpenAI API limits if needed

Your AI Writing Assistant is now live and ready to help users create amazing content! 🚀