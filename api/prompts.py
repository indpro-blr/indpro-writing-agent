"""
Prompt Engineering Module

This module handles all prompt generation and management for the AI Writing Assistant,
including mood-specific instructions, platform specifications, and anti-hallucination strategies.

Constants:
    MOOD_DEFINITIONS: Detailed definitions for all mood types and intensities
    PLATFORM_SPECS: Platform-specific requirements and constraints
    
Functions:
    get_mood_instruction: Generate mood-specific instruction text
    build_mood_combination_prompt: Combine multiple mood instructions
    build_anti_hallucination_prompt: Create comprehensive system prompt
"""

from typing import Dict, List, Any, Optional
import logging
from .utils import setup_logger, estimate_tokens

logger = setup_logger(__name__)

# Mood definitions with 0-10 intensity scales
MOOD_DEFINITIONS = {
    "professional": {
        0: "Extremely casual, informal tone with slang and colloquialisms",
        1: "Very casual, relaxed tone with some informal expressions",
        2: "Casual tone with friendly, approachable language",
        3: "Slightly casual but appropriate for workplace conversations",
        4: "Balanced tone, neither too formal nor too casual",
        5: "Standard professional tone, clear and respectful",
        6: "More formal professional tone with proper business language",
        7: "Formal business tone with industry-appropriate terminology",
        8: "Highly formal, corporate tone with sophisticated language",
        9: "Very formal, executive-level communication style",
        10: "Extremely formal, diplomatic or legal-level precision"
    },
    "enthusiastic": {
        0: "Completely neutral, emotionally flat tone",
        1: "Slightly positive, minimal energy or excitement",
        2: "Mildly positive with subtle enthusiasm",
        3: "Moderately positive with gentle enthusiasm",
        4: "Noticeably positive and encouraging",
        5: "Clearly enthusiastic with energetic language",
        6: "Highly enthusiastic with exclamation and energy",
        7: "Very enthusiastic, passionate and motivating",
        8: "Extremely enthusiastic, inspiring and uplifting",
        9: "Overwhelmingly positive, almost euphoric energy",
        10: "Maximum enthusiasm, explosive excitement and passion"
    },
    "empathetic": {
        0: "Cold, detached, no emotional consideration",
        1: "Slightly acknowledging but emotionally distant",  
        2: "Minimal emotional awareness, brief acknowledgment",
        3: "Some emotional recognition with basic understanding",
        4: "Moderate emotional awareness and consideration",
        5: "Clear empathy with genuine understanding",
        6: "Strong empathy, validating feelings and experiences",
        7: "Deep empathy with comprehensive emotional support",
        8: "Profound empathy, highly attuned to emotional needs",
        9: "Exceptional empathy with therapeutic-level understanding",
        10: "Maximum empathy, completely emotionally aligned"
    },
    "confident": {
        0: "Extremely uncertain, hesitant, and self-doubting",
        1: "Very uncertain with frequent qualifications",
        2: "Somewhat uncertain, cautious language",
        3: "Mildly uncertain with some hesitation",
        4: "Balanced confidence, neither overly certain nor doubtful",
        5: "Clearly confident with assertive language",
        6: "Strong confidence with decisive statements",
        7: "High confidence, authoritative and assured",
        8: "Very confident, commanding and persuasive",
        9: "Extremely confident, powerful and convincing",
        10: "Maximum confidence, absolutely certain and authoritative"
    },
    "creative": {
        0: "Completely conventional, standard, predictable language",
        1: "Mostly conventional with occasional variation",
        2: "Slightly creative with minor unique expressions",
        3: "Moderately creative with some original phrasing",
        4: "Noticeably creative with interesting word choices",
        5: "Clearly creative with unique expressions and metaphors",
        6: "Highly creative with original analogies and imagery",
        7: "Very creative with innovative language and concepts",
        8: "Extremely creative with artistic and poetic elements",
        9: "Overwhelmingly creative, highly artistic expression",
        10: "Maximum creativity, completely original and innovative"
    },
    "urgent": {
        0: "Completely relaxed, no time pressure implied",
        1: "Very relaxed with leisurely pacing",
        2: "Slightly motivated but no real urgency",  
        3: "Moderately paced with gentle encouragement",
        4: "Noticeably motivated with mild time awareness",
        5: "Clear urgency with time-sensitive language",
        6: "Strong urgency, emphasizing immediate action",
        7: "High urgency with compelling calls to action",
        8: "Very urgent, critical and time-pressured",
        9: "Extremely urgent, emergency-level importance",
        10: "Maximum urgency, crisis-level immediate action required"
    },
    "friendly": {
        0: "Cold, distant, unfriendly tone",
        1: "Slightly cool but not hostile",
        2: "Neutral, neither friendly nor unfriendly",
        3: "Mildly friendly with basic politeness",
        4: "Moderately friendly and approachable",
        5: "Clearly friendly with warm language",
        6: "Very friendly, welcoming and personable",
        7: "Highly friendly, genuinely caring and warm",
        8: "Extremely friendly, like talking to a close friend",
        9: "Overwhelmingly friendly, deeply personal connection",
        10: "Maximum friendliness, like family-level warmth"
    },
    "authoritative": {
        0: "No authority, hesitant and deferential",
        1: "Minimal authority, mostly suggestive",
        2: "Slight authority with gentle guidance",
        3: "Moderate authority with clear direction",
        4: "Noticeable authority with firm guidance",
        5: "Clear authority with confident direction",
        6: "Strong authority with commanding presence",
        7: "High authority, expert-level knowledge demonstrated",
        8: "Very authoritative, leadership-level command",
        9: "Extremely authoritative, institutional-level authority",
        10: "Maximum authority, absolute expert and leader"
    },
    "humorous": {
        0: "Completely serious, no humor whatsoever",
        1: "Mostly serious with rare light moments",
        2: "Slightly light-hearted but generally serious",
        3: "Mildly humorous with occasional wit",
        4: "Moderately humorous with gentle humor",
        5: "Clearly humorous with regular witty remarks",
        6: "Quite humorous with frequent clever observations",
        7: "Very humorous, entertaining and amusing",
        8: "Extremely humorous, consistently funny and clever",
        9: "Overwhelmingly humorous, comedy-level entertainment",
        10: "Maximum humor, stand-up comedian level wit"
    },
    "inspiring": {
        0: "Completely uninspiring, potentially discouraging",
        1: "Slightly motivating but generally neutral",
        2: "Mildly encouraging with gentle positivity",
        3: "Moderately inspiring with uplifting elements",
        4: "Noticeably inspiring with motivational language",
        5: "Clearly inspiring with empowering messages",
        6: "Highly inspiring, motivational speaker quality",
        7: "Very inspiring, transformational and uplifting",
        8: "Extremely inspiring, life-changing motivation",
        9: "Overwhelmingly inspiring, spiritual-level guidance",
        10: "Maximum inspiration, legendary motivational impact"
    }
}

# Platform-specific requirements and constraints
PLATFORM_SPECS = {
    "twitter": {
        "character_limit": 280,
        "word_range": {"min": 1, "max": 50},
        "tone": "conversational and engaging",
        "features": ["hashtags encouraged", "mentions possible", "brevity essential"],
        "format": "single tweet format",
        "audience": "general public, broad appeal",
        "style_notes": "punchy, memorable, shareable"
    },
    "linkedin": {
        "character_limit": 3000,
        "word_range": {"min": 10, "max": 300},
        "tone": "professional and networking-focused",
        "features": ["professional insights", "industry relevance", "networking value"],
        "format": "professional post with potential for engagement",
        "audience": "professional network, industry peers",
        "style_notes": "thought leadership, career-focused, industry insights"
    },
    "instagram": {
        "character_limit": 2200,
        "word_range": {"min": 5, "max": 150},
        "tone": "visual and lifestyle-oriented",
        "features": ["hashtags important", "visual context", "story-telling"],
        "format": "caption for visual content",
        "audience": "followers, lifestyle-focused",
        "style_notes": "authentic, personal, visually complementary"
    },
    "facebook": {
        "character_limit": 63206,
        "word_range": {"min": 5, "max": 200},
        "tone": "personal and community-focused",
        "features": ["community engagement", "personal sharing", "longer form possible"],
        "format": "social media post for personal network",
        "audience": "friends, family, local community",
        "style_notes": "personal, conversational, community-minded"
    },
    "blog": {
        "character_limit": None,
        "word_range": {"min": 50, "max": 500},
        "tone": "informative and engaging",
        "features": ["detailed content", "SEO considerations", "reader value"],
        "format": "blog post excerpt or short article",
        "audience": "blog readers, subject matter interested",
        "style_notes": "informative, valuable, well-structured"
    },
    "email": {
        "character_limit": None,
        "word_range": {"min": 20, "max": 400},
        "tone": "direct and purposeful",
        "features": ["clear subject", "actionable content", "professional"],
        "format": "email content with clear purpose",
        "audience": "email recipients, specific target",
        "style_notes": "clear, actionable, respectful of time"
    }
}

def get_mood_instruction(mood_name: str, intensity: int) -> str:
    """
    Generate mood-specific instruction text based on mood and intensity.
    
    Args:
        mood_name (str): Name of the mood (e.g., 'professional', 'enthusiastic')
        intensity (int): Intensity level from 0-10
        
    Returns:
        str: Detailed instruction text for the specified mood and intensity
        
    Raises:
        ValueError: If mood_name is not recognized or intensity is out of range
    """
    if mood_name not in MOOD_DEFINITIONS:
        available_moods = ", ".join(MOOD_DEFINITIONS.keys())
        raise ValueError(f"Unknown mood '{mood_name}'. Available moods: {available_moods}")
    
    if not (0 <= intensity <= 10):
        raise ValueError(f"Intensity must be between 0-10, got {intensity}")
    
    mood_def = MOOD_DEFINITIONS[mood_name]
    return mood_def[intensity]

def build_mood_combination_prompt(mood_values: Dict[str, int]) -> str:
    """
    Combine multiple mood instructions into a cohesive prompt.
    
    Args:
        mood_values (Dict[str, int]): Dictionary mapping mood names to intensity values
        
    Returns:
        str: Combined mood instruction prompt
        
    Raises:
        ValueError: If mood values are invalid
    """
    if not mood_values or not isinstance(mood_values, dict):
        return "Use a neutral, balanced tone throughout."
    
    active_moods = []
    
    for mood_name, intensity in mood_values.items():
        if intensity > 0:  # Only include moods with positive intensity
            try:
                instruction = get_mood_instruction(mood_name, intensity)
                active_moods.append(f"**{mood_name.title()} (Level {intensity})**: {instruction}")
            except ValueError as e:
                logger.warning(f"Skipping invalid mood instruction: {e}")
                continue
    
    if not active_moods:
        return "Use a neutral, balanced tone throughout."
    
    mood_prompt = "TONE AND STYLE REQUIREMENTS:\n"
    mood_prompt += "Apply the following mood characteristics to your writing:\n\n"
    mood_prompt += "\n".join(active_moods)
    mood_prompt += "\n\nBalance these characteristics harmoniously - if moods conflict, prioritize the higher intensity values while maintaining coherence."
    
    return mood_prompt

def build_anti_hallucination_prompt(description: str, mood_values: Dict[str, int], platform: str) -> str:
    """
    Create a comprehensive system prompt with anti-hallucination strategies.
    
    This function builds a detailed prompt that:
    - Prevents AI from revealing its nature
    - Ensures content stays focused on the description
    - Applies mood and platform requirements
    - Includes quality and safety guidelines
    
    Args:
        description (str): User's content description/topic
        mood_values (Dict[str, int]): Mood intensity settings
        platform (str): Target platform for the content
        
    Returns:
        str: Complete system prompt for content generation
        
    Raises:
        ValueError: If required parameters are missing or invalid
    """
    if not description or not description.strip():
        raise ValueError("Description cannot be empty")
    
    if platform not in PLATFORM_SPECS:
        available_platforms = ", ".join(PLATFORM_SPECS.keys())
        raise ValueError(f"Unknown platform '{platform}'. Available platforms: {available_platforms}")
    
    # Get platform specifications
    platform_spec = PLATFORM_SPECS[platform]
    
    # Build mood instructions
    mood_instructions = build_mood_combination_prompt(mood_values)
    
    # Build comprehensive system prompt
    system_prompt = f"""You are a professional content writer creating content for {platform}. 

CRITICAL REQUIREMENTS:
1. NEVER mention that you are an AI, language model, or assistant
2. NEVER use phrases like "as an AI", "I can't", "I don't have access to", etc.
3. Write ONLY about the specified topic - do not add disclaimers or meta-commentary
4. Focus exclusively on: {description}

PLATFORM SPECIFICATIONS for {platform.upper()}:
- Target audience: {platform_spec['audience']}
- Tone: {platform_spec['tone']}
- STRICT Word count: {platform_spec['word_range']['min']}-{platform_spec['word_range']['max']} words (THIS IS MANDATORY)
- Style notes: {platform_spec['style_notes']}
- Key features: {', '.join(platform_spec['features'])}

{mood_instructions}

CONTENT QUALITY STANDARDS:
- Write original, engaging content that directly addresses the topic
- Use natural, human-like language appropriate for the platform
- Ensure content is factual and avoid making unverifiable claims
- CRITICAL: Stay within the EXACT word count range ({platform_spec['word_range']['min']}-{platform_spec['word_range']['max']} words) - count words carefully
- Make every word count - be concise but impactful
- End with a natural conclusion - no generic endings

WHAT NOT TO DO:
- Don't ask questions back to the user
- Don't offer to help with other tasks
- Don't explain what you're doing
- Don't use placeholder text like "[Insert content here]"
- Don't include meta-instructions or self-references
- Don't add disclaimers about being an AI

Create compelling, focused content that serves the specified purpose for {platform}."""
    
    return system_prompt

def validate_prompt_length(prompt: str, max_tokens: int = 3000) -> bool:
    """
    Validate that prompt length is within acceptable token limits.
    
    Args:
        prompt (str): Prompt text to validate
        max_tokens (int): Maximum allowed tokens
        
    Returns:
        bool: True if prompt is within limits
    """
    estimated_tokens = estimate_tokens(prompt)
    if estimated_tokens > max_tokens:
        logger.warning(f"Prompt length ({estimated_tokens} tokens) exceeds limit ({max_tokens} tokens)")
        return False
    return True

def get_platform_word_limit(platform: str) -> Dict[str, int]:
    """
    Get word count limits for a specific platform.
    
    Args:
        platform (str): Platform name
        
    Returns:
        Dict[str, int]: Dictionary with 'min' and 'max' word limits
        
    Raises:
        ValueError: If platform is not recognized
    """
    if platform not in PLATFORM_SPECS:
        available_platforms = ", ".join(PLATFORM_SPECS.keys())
        raise ValueError(f"Unknown platform '{platform}'. Available platforms: {available_platforms}")
    
    return PLATFORM_SPECS[platform]["word_range"]

def get_available_moods() -> List[str]:
    """
    Get list of all available mood types.
    
    Returns:
        List[str]: List of mood names
    """
    return list(MOOD_DEFINITIONS.keys())

def get_available_platforms() -> List[str]:
    """
    Get list of all available platforms.
    
    Returns:
        List[str]: List of platform names
    """
    return list(PLATFORM_SPECS.keys())

def create_mood_summary(mood_values: Dict[str, int]) -> str:
    """
    Create a human-readable summary of active moods.
    
    Args:
        mood_values (Dict[str, int]): Mood intensity settings
        
    Returns:
        str: Summary of active moods and their intensities
    """
    if not mood_values:
        return "No specific mood settings applied"
    
    active_moods = [(mood, intensity) for mood, intensity in mood_values.items() if intensity > 0]
    
    if not active_moods:
        return "No active moods (all set to 0)"
    
    # Sort by intensity (highest first)
    active_moods.sort(key=lambda x: x[1], reverse=True)
    
    mood_descriptions = []
    for mood, intensity in active_moods:
        if intensity >= 8:
            level_desc = "Very High"
        elif intensity >= 6:
            level_desc = "High"
        elif intensity >= 4:
            level_desc = "Moderate"
        elif intensity >= 2:
            level_desc = "Low"
        else:
            level_desc = "Minimal"
        
        mood_descriptions.append(f"{mood.title()} ({level_desc} - {intensity}/10)")
    
    return "Active moods: " + ", ".join(mood_descriptions)

# Validation functions for prompt engineering
def validate_mood_combination(mood_values: Dict[str, int]) -> List[str]:
    """
    Validate mood combination and return any warnings.
    
    Args:
        mood_values (Dict[str, int]): Mood settings to validate
        
    Returns:
        List[str]: List of validation warnings (empty if no issues)
    """
    warnings = []
    
    # Check for conflicting moods at high intensities
    if mood_values.get("professional", 0) >= 8 and mood_values.get("humorous", 0) >= 8:
        warnings.append("Very high professional and humorous moods may conflict")
    
    if mood_values.get("urgent", 0) >= 8 and mood_values.get("friendly", 0) >= 8:
        warnings.append("Very high urgency with high friendliness may seem inconsistent")
    
    if mood_values.get("empathetic", 0) >= 8 and mood_values.get("authoritative", 0) >= 8:
        warnings.append("Very high empathy with high authority may be challenging to balance")
    
    # Check for too many high-intensity moods
    high_intensity_count = sum(1 for intensity in mood_values.values() if intensity >= 7)
    if high_intensity_count > 3:
        warnings.append(f"Too many high-intensity moods ({high_intensity_count}) may result in conflicting tone")
    
    return warnings


def create_system_prompt(mood_values: Dict[str, int], platform: str) -> str:
    """
    Create a system prompt for the AI writing assistant.
    
    Args:
        mood_values: Dictionary of mood settings (0-10)
        platform: Target platform for content
        
    Returns:
        str: Complete system prompt
    """
    # Get platform info
    platform_info = PLATFORM_SPECS.get(platform, PLATFORM_SPECS['blog'])
    
    # Build mood instructions
    mood_prompt = build_mood_combination_prompt(mood_values)
    
    # Create system prompt
    system_prompt = f"""You are an expert content writer specializing in creating engaging, platform-optimized content with precise mood and tone control.

PLATFORM: {platform.upper()}
- Word range: {platform_info['word_range']['min']}-{platform_info['word_range']['max']} words
- Tone: {platform_info['tone']}
- Style notes: {platform_info['style_notes']}
- Key features: {', '.join(platform_info['features'])}

MOOD & TONE INSTRUCTIONS:
{mood_prompt}

CONTENT REQUIREMENTS:
1. Stay within the specified word range for {platform}
2. Apply the mood combination naturally throughout the content
3. Use platform-appropriate formatting and style
4. Focus on the user's specific topic and requirements
5. Ensure content is engaging and valuable to the target audience

QUALITY STANDARDS:
- Clear, coherent, and well-structured
- Appropriate for the platform's audience
- Reflects the specified mood combination
- Actionable and valuable content
- No filler or unnecessary repetition

Generate content that perfectly balances all specified moods while meeting platform requirements."""

    return system_prompt


def create_user_prompt(description: str, mood_values: Dict[str, int], platform: str) -> str:
    """
    Create a user prompt with the content request.
    
    Args:
        description: User's content description
        mood_values: Dictionary of mood settings
        platform: Target platform
        
    Returns:
        str: Complete user prompt
    """
    # Get mood summary for context
    mood_summary = create_mood_summary(mood_values)
    
    # Get platform word limits
    platform_info = PLATFORM_SPECS.get(platform, PLATFORM_SPECS['blog'])
    word_range = f"{platform_info['word_range']['min']}-{platform_info['word_range']['max']}"
    
    user_prompt = f"""Please create content for {platform} with the following specifications:

TOPIC/DESCRIPTION:
{description}

REQUIREMENTS:
- Platform: {platform}
- Word count: {word_range} words
- Mood profile: {mood_summary}
- Tone: {platform_info['tone']}
- Style: {platform_info['style_notes']}

Create engaging, valuable content that perfectly matches these specifications."""

    return user_prompt