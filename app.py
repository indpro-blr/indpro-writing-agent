"""
AI Writing Assistant - Streamlit Application

A comprehensive web interface for AI-powered content generation with mood-based
customization and platform-specific optimization.

This application provides:
- Interactive mood sliders for tone customization
- Platform-specific content generation
- Real-time word count and validation
- Responsive design for desktop and mobile
- Generation history and export functionality

Author: AI Writing Assistant Team
Version: 1.0.0
"""

import streamlit as st

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="AI Writing Assistant",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/ai-writing-assistant',
        'Report a bug': 'https://github.com/yourusername/ai-writing-assistant/issues',
        'About': "AI Writing Assistant v1.0.0 - Generate mood-customized content for any platform"
    }
)

# Now import other modules
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Import API modules with graceful fallback
try:
    from api import run_writing_agent, get_config
    from api.prompts import get_available_moods, get_available_platforms, create_mood_summary
    from api.utils import count_words, validate_word_count, setup_logger
    API_AVAILABLE = True
except ImportError as e:
    st.error(f"API modules not available: {e}")
    API_AVAILABLE = False

# Initialize logger
logger = setup_logger(__name__) if API_AVAILABLE else logging.getLogger(__name__)

# Custom CSS for responsive design and styling
st.markdown("""
<style>
    /* Main container styling */
    .main > div {
        padding-top: 2rem;
        background-color: #ffffff;
        color: #000000;
    }
    
    /* Custom styling for mood sliders */
    .mood-slider-container {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #2a5b51;
        border: 1px solid #2a5b51;
    }
    
    /* Platform selector styling */
    .platform-container {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #2a5b51;
        border: 1px solid #2a5b51;
        color: #000000;
    }
    
    /* Output container styling */
    .output-container {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #2a5b51;
        border: 1px solid #2a5b51;
        color: #000000;
    }
    
    /* Success message styling */
    .success-message {
        background-color: #2a5b51;
        color: #ffffff;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #2a5b51;
        margin: 1rem 0;
    }
    
    /* Error message styling */
    .error-message {
        background-color: #000000;
        color: #ffffff;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #000000;
        margin: 1rem 0;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main > div {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .mood-slider-container,
        .platform-container,
        .output-container {
            margin: 0.5rem 0;
            padding: 1rem;
        }
    }
    
    /* Character counter styling */
    .char-counter {
        font-size: 0.8rem;
        color: #000000;
        text-align: right;
        margin-top: 0.5rem;
    }
    
    /* Mood preset buttons */
    .preset-button {
        margin: 0.25rem;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        border: 1px solid #2a5b51;
        background-color: #ffffff;
        color: #000000;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    /* Copy button styling */
    .copy-button-container {
        position: relative;
    }
    
    /* Success feedback for copy operation */
    .copy-success {
        background-color: #2a5b51;
        color: #ffffff;
        border: 1px solid #2a5b51;
        border-radius: 5px;
        padding: 0.5rem;
        margin-top: 0.5rem;
        animation: fadeIn 0.3s ease-in-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .preset-button:hover {
        background-color: #2a5b51;
        color: #ffffff;
        border-color: #2a5b51;
    }
    
    /* Generation history styling */
    .history-item {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #2a5b51;
        border: 1px solid #2a5b51;
        color: #000000;
    }
    
    /* Loading animation */
    .loading-text {
        animation: pulse 1.5s ease-in-out infinite alternate;
        color: #000000;
    }
    
    @keyframes pulse {
        from { opacity: 1; }
        to { opacity: 0.5; }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables."""
    if 'mood_values' not in st.session_state:
        st.session_state.mood_values = {
            'professional': 5,
            'enthusiastic': 3,
            'empathetic': 3,
            'confident': 5,
            'creative': 4,
            'urgent': 2,
            'friendly': 4,
            'authoritative': 3,
            'humorous': 2,
            'inspiring': 3
        }
    
    if 'generation_history' not in st.session_state:
        st.session_state.generation_history = []
    
    if 'current_output' not in st.session_state:
        st.session_state.current_output = ""
    
    if 'last_request_id' not in st.session_state:
        st.session_state.last_request_id = None
    
    if 'generation_metadata' not in st.session_state:
        st.session_state.generation_metadata = {}

# Mood preset configurations
MOOD_PRESETS = {
    "Professional Business": {
        "professional": 8, "confident": 7, "authoritative": 6,
        "enthusiastic": 2, "empathetic": 3, "creative": 2,
        "urgent": 3, "friendly": 3, "humorous": 1, "inspiring": 4
    },
    "Friendly & Approachable": {
        "friendly": 8, "empathetic": 7, "enthusiastic": 6,
        "professional": 4, "confident": 5, "creative": 4,
        "urgent": 2, "authoritative": 2, "humorous": 5, "inspiring": 5
    },
    "Creative & Inspiring": {
        "creative": 9, "inspiring": 8, "enthusiastic": 7,
        "professional": 3, "confident": 6, "empathetic": 5,
        "urgent": 3, "authoritative": 3, "friendly": 6, "humorous": 4
    },
    "Urgent & Direct": {
        "urgent": 8, "confident": 8, "authoritative": 7,
        "professional": 6, "enthusiastic": 5, "empathetic": 3,
        "creative": 2, "friendly": 3, "humorous": 1, "inspiring": 4
    },
    "Balanced & Neutral": {
        "professional": 5, "enthusiastic": 4, "empathetic": 4,
        "confident": 5, "creative": 4, "urgent": 3,
        "friendly": 5, "authoritative": 4, "humorous": 3, "inspiring": 4
    }
}

def apply_mood_preset(preset_name: str):
    """Apply a mood preset to session state."""
    if preset_name in MOOD_PRESETS:
        st.session_state.mood_values.update(MOOD_PRESETS[preset_name])
        st.rerun()

def reset_all_moods():
    """Reset all mood values to neutral (5 or appropriate default)."""
    st.session_state.mood_values = {
        'professional': 5, 'enthusiastic': 3, 'empathetic': 3,
        'confident': 5, 'creative': 4, 'urgent': 2,
        'friendly': 4, 'authoritative': 3, 'humorous': 2, 'inspiring': 3
    }
    st.rerun()

def render_header():
    """Render the application header and description."""
    st.title("AI Writing Assistant")
    st.markdown("""
    <div style="background: linear-gradient(90deg, #2a5b51 0%, #000000 100%); 
                padding: 1.5rem; border-radius: 10px; color: white; margin-bottom: 2rem;">
        <h3 style="margin: 0; color: white;">Generate Perfect Content for Any Platform</h3>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
            Customize tone with 10 different mood settings and optimize for your target platform.
            From professional LinkedIn posts to creative Instagram captions, get content that fits perfectly.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_description_input():
    """Render the description input section."""
    st.subheader("Describe Your Content")
    
    # Description text area
    description = st.text_area(
        "What would you like to write about?",
        placeholder="Example: Write about the benefits of remote work for productivity and work-life balance...",
        height=120,
        help="Provide a clear description of the content you want to generate. Be specific about the topic, key points, or message you want to convey."
    )
    
    # Character counter
    char_count = len(description) if description else 0
    max_chars = 2000
    color = "#000000" if char_count > max_chars else "#2a5b51" if char_count > 10 else "#000000"
    
    st.markdown(f"""
    <div class="char-counter">
        <span style="color: {color};">{char_count}/{max_chars} characters</span>
        {" Good length" if 10 <= char_count <= max_chars else 
         " Too long" if char_count > max_chars else 
         " Too short (minimum 10 characters)" if char_count > 0 else ""}
    </div>
    """, unsafe_allow_html=True)
    
    return description

def render_mood_sliders():
    """Render the mood customization sliders."""
    st.subheader("Customize Tone & Mood")
    
    # Mood preset buttons
    st.markdown("**Quick Presets:**")
    cols = st.columns(len(MOOD_PRESETS))
    for i, preset_name in enumerate(MOOD_PRESETS.keys()):
        with cols[i]:
            if st.button(preset_name, key=f"preset_{i}", use_container_width=True):
                apply_mood_preset(preset_name)
    
    # Reset button
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("Reset All", use_container_width=True):
            reset_all_moods()
    
    st.markdown("---")
    
    # Mood sliders in two columns
    col1, col2 = st.columns(2)
    
    mood_descriptions = {
        'professional': 'How formal and business-appropriate should the tone be?',
        'enthusiastic': 'How much energy and excitement should be conveyed?',
        'empathetic': 'How much emotional understanding and care should be shown?',
        'confident': 'How certain and assertive should the messaging be?',
        'creative': 'How original and innovative should the language be?',
        'urgent': 'How time-sensitive and action-oriented should it feel?',
        'friendly': 'How warm and approachable should the tone be?',
        'authoritative': 'How much expertise and leadership should be demonstrated?',
        'humorous': 'How much wit and lightness should be included?',
        'inspiring': 'How motivational and uplifting should the message be?'
    }
    
    moods = list(st.session_state.mood_values.keys())
    
    # First column moods
    with col1:
        for mood in moods[:5]:
            st.session_state.mood_values[mood] = st.slider(
                f"**{mood.title()}**",
                min_value=0,
                max_value=10,
                value=st.session_state.mood_values[mood],
                help=mood_descriptions.get(mood, f"Adjust {mood} intensity"),
                key=f"slider_{mood}"
            )
    
    # Second column moods
    with col2:
        for mood in moods[5:]:
            st.session_state.mood_values[mood] = st.slider(
                f"**{mood.title()}**",
                min_value=0,
                max_value=10,
                value=st.session_state.mood_values[mood],
                help=mood_descriptions.get(mood, f"Adjust {mood} intensity"),
                key=f"slider_{mood}"
            )
    
    # Active moods summary
    active_moods = [(mood, value) for mood, value in st.session_state.mood_values.items() if value > 5]
    if active_moods:
        active_moods.sort(key=lambda x: x[1], reverse=True)
        mood_summary = ", ".join([f"{mood.title()} ({value})" for mood, value in active_moods[:3]])
        st.info(f"**Dominant moods:** {mood_summary}")

def render_platform_selector():
    """Render the platform selection interface."""
    st.subheader("Choose Your Platform")
    
    if not API_AVAILABLE:
        platforms = ['twitter', 'linkedin', 'instagram', 'facebook', 'blog', 'email']
    else:
        platforms = get_available_platforms()
    
    platform_descriptions = {
        'twitter': 'Twitter: Short, engaging posts (1-50 words) - Perfect for quick thoughts and viral content',
        'linkedin': 'LinkedIn: Professional content (10-300 words) - Industry insights and networking',
        'instagram': 'Instagram: Visual-friendly captions (5-150 words) - Lifestyle and storytelling',
        'facebook': 'Facebook: Community posts (5-200 words) - Personal sharing and group discussions',
        'blog': 'Blog: Informative articles (50-500 words) - Detailed content and thought leadership',
        'email': 'Email: Direct communication (20-400 words) - Clear and actionable messaging'
    }
    
    # Platform selection with visual cards
    selected_platform = st.selectbox(
        "Select your target platform:",
        platforms,
        format_func=lambda x: platform_descriptions.get(x, x).split(' - ')[0],
        help="Choose the platform where you'll publish this content. Each platform has different requirements and best practices."
    )
    
    # Platform-specific guidance
    if selected_platform in platform_descriptions:
        description = platform_descriptions[selected_platform]
        st.markdown(f"""
        <div class="platform-container">
            <strong>{description.split(' - ')[0]}</strong><br>
            <em>{description.split(' - ')[1] if ' - ' in description else ''}</em>
        </div>
        """, unsafe_allow_html=True)
    
    return selected_platform

def render_generation_interface(description: str, platform: str):
    """Render the content generation interface."""
    st.subheader("Generate Content")
    
    # Validate inputs
    can_generate = bool(description and len(description.strip()) >= 10 and platform)
    
    if not can_generate:
        if not description or len(description.strip()) < 10:
            st.warning("Please provide a description of at least 10 characters.")
        if not platform:
            st.warning("Please select a target platform.")
    
    # Generation button
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        generate_button = st.button(
            "Generate Content",
            disabled=not can_generate or not API_AVAILABLE,
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        if st.session_state.current_output:
            regenerate_button = st.button("Regenerate", use_container_width=True)
        else:
            regenerate_button = False
    
    # Handle generation
    if (generate_button or regenerate_button) and API_AVAILABLE:
        generate_content(description, platform)
    
    # Handle generation for unavailable API
    if (generate_button or regenerate_button) and not API_AVAILABLE:
        st.error("API modules not available. Please install required dependencies.")

def generate_content(description: str, platform: str):
    """Generate content using the API."""
    with st.spinner("Generating your content..."):
        try:
            # Add loading message
            loading_placeholder = st.empty()
            loading_placeholder.markdown(
                '<div class="loading-text">Crafting your content with the perfect mood and tone...</div>',
                unsafe_allow_html=True
            )
            
            # Call the API
            result = run_writing_agent(
                description=description,
                mood_values=st.session_state.mood_values,
                platform=platform,
                max_retries=2
            )
            
            loading_placeholder.empty()
            
            # Handle results
            if result['success']:
                st.session_state.current_output = result['content']
                st.session_state.last_request_id = result['request_id']
                st.session_state.generation_metadata = result['metadata']
                
                # Add to history
                history_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'description': description,
                    'platform': platform,
                    'mood_values': st.session_state.mood_values.copy(),
                    'content': result['content'],
                    'word_count': result['word_count'],
                    'request_id': result['request_id']
                }
                st.session_state.generation_history.insert(0, history_entry)
                
                # Keep only last 10 generations
                st.session_state.generation_history = st.session_state.generation_history[:10]
                
                st.success("Content generated successfully!")
                
            else:
                st.error(f"Generation failed: {result['error_message']}")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            logger.error(f"Content generation error: {e}")

def render_output_section():
    """Render the generated content output section."""
    if st.session_state.current_output:
        st.subheader("Generated Content")
        
        # Output container
        st.markdown(f"""
        <div class="output-container">
            <div style="white-space: pre-wrap; font-size: 1.1rem; line-height: 1.6;">
{st.session_state.current_output}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Content metrics
        word_count = count_words(st.session_state.current_output) if API_AVAILABLE else len(st.session_state.current_output.split())
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Word Count", word_count)
        
        with col2:
            char_count = len(st.session_state.current_output)
            st.metric("Characters", char_count)
        
        with col3:
            if st.session_state.generation_metadata:
                processing_time = st.session_state.generation_metadata.get('processing_time_seconds', 0)
                st.metric("Generation Time", f"{processing_time:.1f}s")
        
        with col4:
            if st.session_state.generation_metadata:
                retries = st.session_state.generation_metadata.get('total_retries', 0)
                st.metric("API Retries", retries)
        
        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            # Copy to clipboard functionality
            copy_button_key = f"copy_button_{hash(st.session_state.current_output)}"
            if st.button("Copy", key=copy_button_key, use_container_width=True):
                # Create a unique ID for this copy operation
                copy_id = f"copy_content_{int(time.time() * 1000)}"
                
                # Prepare content for JavaScript (escape special characters)
                content_to_copy = (st.session_state.current_output
                                 .replace('\\', '\\\\')
                                 .replace('`', '\\`')
                                 .replace('$', '\\$'))
                
                # Enhanced clipboard implementation with better fallbacks
                st.markdown(f"""
                <div id="{copy_id}" style="display: none;">{st.session_state.current_output}</div>
                <script>
                (function() {{
                    const text = `{content_to_copy}`;
                    const copyId = '{copy_id}';
                    
                    function copyToClipboard() {{
                        if (navigator.clipboard && window.isSecureContext) {{
                            // Modern Clipboard API
                            navigator.clipboard.writeText(text).then(function() {{
                                console.log('Text copied to clipboard successfully');
                            }}).catch(function(err) {{
                                console.log('Failed to copy using Clipboard API, trying fallback');
                                fallbackCopyTextToClipboard();
                            }});
                        }} else {{
                            // Fallback for older browsers or non-secure contexts
                            fallbackCopyTextToClipboard();
                        }}
                    }}
                    
                    function fallbackCopyTextToClipboard() {{
                        const textArea = document.createElement("textarea");
                        textArea.value = text;
                        
                        // Make the textarea out of viewport
                        textArea.style.position = "fixed";
                        textArea.style.left = "-999999px";
                        textArea.style.top = "-999999px";
                        
                        document.body.appendChild(textArea);
                        textArea.focus();
                        textArea.select();
                        
                        try {{
                            const successful = document.execCommand('copy');
                            if (successful) {{
                                console.log('Fallback: Text copied to clipboard');
                            }} else {{
                                console.log('Fallback: Copy command was unsuccessful');
                            }}
                        }} catch (err) {{
                            console.error('Fallback: Unable to copy to clipboard', err);
                        }}
                        
                        document.body.removeChild(textArea);
                    }}
                    
                    // Execute copy immediately
                    copyToClipboard();
                    
                    // Clean up the hidden div after a short delay
                    setTimeout(function() {{
                        const element = document.getElementById(copyId);
                        if (element) {{
                            element.remove();
                        }}
                    }}, 1000);
                }})();
                </script>
                """, unsafe_allow_html=True)
                
                st.success("Content copied to clipboard!")
        
        with col2:
            # Download as text file
            if st.download_button(
                label="Download",
                data=st.session_state.current_output,
                file_name=f"ai_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            ):
                st.success("Content downloaded!")

def render_sidebar():
    """Render the sidebar with additional features."""
    with st.sidebar:
        st.header("Session Info")
        
        # Generation statistics
        total_generations = len(st.session_state.generation_history)
        st.metric("Total Generations", total_generations)
        
        if st.session_state.generation_metadata:
            st.metric("Last Model", st.session_state.generation_metadata.get('model_name', 'N/A'))
        
        # Current mood summary
        st.header("Current Mood Profile")
        if API_AVAILABLE:
            mood_summary = create_mood_summary(st.session_state.mood_values)
            st.write(mood_summary)
        else:
            active_moods = [f"{mood}: {value}" for mood, value in st.session_state.mood_values.items() if value > 5]
            if active_moods:
                st.write("Active moods:")
                for mood in active_moods[:5]:  # Show top 5
                    st.write(f"• {mood}")
        
        # Generation history
        if st.session_state.generation_history:
            st.header("Recent Generations")
            
            for i, entry in enumerate(st.session_state.generation_history[:5]):
                with st.expander(f"{entry['platform'].title()} - {entry['timestamp'][:10]}"):
                    st.write(f"**Description:** {entry['description'][:100]}...")
                    st.write(f"**Words:** {entry['word_count']}")
                    if st.button(f"Reuse Settings", key=f"reuse_{i}"):
                        st.session_state.mood_values = entry['mood_values']
                        st.rerun()
        
        # Settings and help
        st.header("Settings")
        
        if st.button("Clear History"):
            st.session_state.generation_history = []
            st.rerun()
        
        if st.button("Reset All Settings"):
            reset_all_moods()
            st.session_state.current_output = ""
            st.rerun()
        
        # Help section
        with st.expander("Help & Tips"):
            st.markdown("""
            **Getting Better Results:**
            - Be specific in your descriptions
            - Experiment with different mood combinations
            - Consider your target audience
            - Use platform-specific presets
            
            **Mood Tips:**
            - Professional + Authoritative = Business leadership
            - Creative + Inspiring = Motivational content  
            - Friendly + Humorous = Social media posts
            - Urgent + Confident = Call-to-action content
            """)

def render_footer():
    """Render the application footer."""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #000000; padding: 1rem;">
        <p>AI Writing Assistant v1.0.0 | Made using Streamlit & LangGraph</p>
        <p><small>Generate amazing content with AI-powered mood customization</small></p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Render main interface
    render_header()
    
    # Main content area
    description = render_description_input()
    
    render_mood_sliders()
    
    platform = render_platform_selector()
    
    render_generation_interface(description, platform)
    
    render_output_section()
    
    # Sidebar
    render_sidebar()
    
    # Footer
    render_footer()

if __name__ == "__main__":
    main()