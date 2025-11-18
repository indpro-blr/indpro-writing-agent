"""
LangGraph Agent Implementation

This module implements the core AI Writing Assistant workflow using LangGraph
state machines for reliable, traceable content generation with retry logic
and comprehensive error handling.

Classes:
    AgentState: TypedDict defining the state structure
    
Functions:
    create_workflow: Build and compile the LangGraph workflow
    run_writing_agent: Main entry point for content generation
"""

import asyncio
import time
from typing import Dict, Any, Optional, TypedDict, List
from typing_extensions import Annotated
import logging

try:
    from langgraph.graph import StateGraph, END
    from langgraph.graph.message import add_messages
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage
except ImportError as e:
    # Graceful fallback for development without dependencies
    logging.warning(f"LangGraph dependencies not available: {e}")
    StateGraph = None
    END = "END"
    add_messages = None
    ChatOpenAI = None
    HumanMessage = None 
    SystemMessage = None

from .config import get_config, ConfigurationError
from .prompts import (
    build_anti_hallucination_prompt,
    validate_prompt_length,
    get_platform_word_limit,
    validate_mood_combination
)
from .utils import (
    setup_logger,
    count_words,
    validate_word_count,
    detect_hallucination_markers,
    sanitize_input,
    create_request_id,
    format_error_message
)

logger = setup_logger(__name__)

class AgentState(TypedDict):
    """
    State definition for the LangGraph workflow.
    
    This TypedDict defines all the state variables that flow through
    the agent workflow nodes.
    """
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

# Node implementations

def validate_input(state: AgentState) -> AgentState:
    """
    Validate input parameters and prepare state for processing.
    
    Args:
        state (AgentState): Current workflow state
        
    Returns:
        AgentState: Updated state with validation results
    """
    logger.info(f"[{state['request_id']}] Starting input validation")
    
    try:
        # Sanitize description
        description = sanitize_input(state["description"])
        if not description or len(description.strip()) < 10:
            raise ValueError("Description must be at least 10 characters long")
        
        if len(description) > 2000:
            raise ValueError("Description must be less than 2000 characters")
        
        # Validate platform
        platform = state["platform"].lower()
        from .prompts import get_available_platforms
        if platform not in get_available_platforms():
            raise ValueError(f"Invalid platform: {platform}")
        
        # Validate mood values
        mood_values = state["mood_values"]
        if not isinstance(mood_values, dict):
            raise ValueError("Mood values must be a dictionary")
        
        for mood, value in mood_values.items():
            if not isinstance(value, int) or not (0 <= value <= 10):
                raise ValueError(f"Mood value for '{mood}' must be integer between 0-10")
        
        # Check for mood conflicts
        warnings = validate_mood_combination(mood_values)
        if warnings:
            logger.warning(f"[{state['request_id']}] Mood validation warnings: {warnings}")
            state["metadata"]["mood_warnings"] = warnings
        
        # Update state with validated inputs
        state["description"] = description
        state["platform"] = platform
        state["validation_passed"] = True
        state["metadata"]["validation_status"] = "passed"
        
        logger.info(f"[{state['request_id']}] Input validation successful")
        
    except Exception as e:
        logger.error(f"[{state['request_id']}] Input validation failed: {e}")
        state["validation_passed"] = False
        state["error_message"] = format_error_message(e, "Input validation")
        state["metadata"]["validation_status"] = "failed"
    
    return state

def build_context(state: AgentState) -> AgentState:
    """
    Build the system prompt and context for content generation.
    
    Args:
        state (AgentState): Current workflow state
        
    Returns:
        AgentState: Updated state with system prompt
    """
    logger.info(f"[{state['request_id']}] Building context and system prompt")
    
    try:
        # Build comprehensive system prompt
        system_prompt = build_anti_hallucination_prompt(
            description=state["description"],
            mood_values=state["mood_values"],
            platform=state["platform"]
        )
        
        # Validate prompt length
        if not validate_prompt_length(system_prompt):
            raise ValueError("Generated system prompt is too long")
        
        state["system_prompt"] = system_prompt
        state["metadata"]["prompt_length"] = len(system_prompt)
        
        logger.info(f"[{state['request_id']}] Context building successful")
        
    except Exception as e:
        logger.error(f"[{state['request_id']}] Context building failed: {e}")
        state["error_message"] = format_error_message(e, "Context building")
        
    return state

def generate_content(state: AgentState) -> AgentState:
    """
    Generate content using OpenAI API with retry logic.
    
    Args:
        state (AgentState): Current workflow state
        
    Returns:
        AgentState: Updated state with generated content
    """
    request_id = state["request_id"]
    retry_count = state["retry_count"]
    
    logger.info(f"[{request_id}] Generating content (attempt {retry_count + 1})")
    
    # Clear previous error messages for new attempts
    state["error_message"] = ""
    
    try:
        config = get_config()
        
        # Initialize OpenAI client
        if ChatOpenAI is None:
            raise ImportError("LangChain OpenAI dependencies not available")
            
        llm = ChatOpenAI(
            api_key=config.OPENAI_API_KEY,
            model=config.MODEL_NAME,
            max_tokens=config.MAX_TOKENS,
            temperature=config.TEMPERATURE,
            top_p=config.TOP_P,
            timeout=config.TIMEOUT
        )
        
        # Prepare messages
        messages = [
            SystemMessage(content=state["system_prompt"]),
            HumanMessage(content=f"Create content about: {state['description']}")
        ]
        
        # Generate content with exponential backoff
        backoff_delay = min(2 ** retry_count, 16)  # Cap at 16 seconds
        if retry_count > 0:
            logger.info(f"[{request_id}] Waiting {backoff_delay}s before retry")
            time.sleep(backoff_delay)
        
        # Make API call
        response = llm.invoke(messages)
        generated_content = response.content.strip()
        
        if not generated_content:
            raise ValueError("Generated content is empty")
        
        state["generated_content"] = generated_content
        state["word_count"] = count_words(generated_content)
        state["metadata"]["generation_successful"] = True
        state["metadata"]["api_response_length"] = len(generated_content)
        
        logger.info(f"[{request_id}] Content generation successful ({state['word_count']} words)")
        
    except Exception as e:
        logger.error(f"[{request_id}] Content generation failed: {e}")
        state["error_message"] = format_error_message(e, "Content generation")
        state["metadata"]["generation_successful"] = False
        
        # Increment retry count for generation failures
        state["retry_count"] += 1
    
    return state

def quality_check(state: AgentState) -> AgentState:  
    """
    Perform quality checks on generated content.
    
    Args:
        state (AgentState): Current workflow state
        
    Returns:
        AgentState: Updated state with quality assessment
    """
    request_id = state["request_id"]
    logger.info(f"[{request_id}] Performing quality checks")
    
    try:
        content = state["generated_content"]
        platform = state["platform"]
        
        # Check for hallucination markers
        hallucination_markers = detect_hallucination_markers(content)
        state["hallucination_markers"] = hallucination_markers
        
        # Check platform compliance
        platform_compliant = validate_word_count(content, platform)
        state["platform_compliant"] = platform_compliant
        
        # Overall quality assessment
        quality_issues = []
        
        if hallucination_markers:
            quality_issues.append(f"Detected {len(hallucination_markers)} hallucination markers")
        
        # Be more lenient with word count after multiple retries
        retry_count = state["retry_count"]
        if not platform_compliant:
            word_limits = get_platform_word_limit(platform)
            
            # After 3+ retries, be more flexible with word count limits
            if retry_count >= 3:
                # Allow up to 25% variance from limits
                flexible_min = int(word_limits['min'] * 0.75)
                flexible_max = int(word_limits['max'] * 1.25)
                
                if flexible_min <= state['word_count'] <= flexible_max:
                    logger.info(f"[{request_id}] Accepting content with flexible word count after {retry_count} retries")
                    platform_compliant = True
                    state["platform_compliant"] = True
                else:
                    quality_issues.append(
                        f"Word count ({state['word_count']}) not within flexible {platform} limits "
                        f"({flexible_min}-{flexible_max}) after {retry_count} retries"
                    )
            else:
                quality_issues.append(
                    f"Word count ({state['word_count']}) not within {platform} limits "
                    f"({word_limits['min']}-{word_limits['max']})"
                )
        
        # Check for empty or very short content
        if state["word_count"] < 5:
            quality_issues.append("Generated content is too short")
        
        # Determine if quality check passed
        if quality_issues:
            state["validation_passed"] = False
            state["error_message"] = "Quality check failed: " + "; ".join(quality_issues)
            logger.warning(f"[{request_id}] Quality issues found: {quality_issues}")
        else:
            state["validation_passed"] = True
            logger.info(f"[{request_id}] Quality check passed")
        
        state["metadata"]["quality_issues"] = quality_issues
        
    except Exception as e:
        logger.error(f"[{request_id}] Quality check error: {e}")
        state["validation_passed"] = False
        state["error_message"] = format_error_message(e, "Quality check")
    
    return state

def format_output(state: AgentState) -> AgentState:
    """
    Format the final output and add metadata.
    
    Args:
        state (AgentState): Current workflow state
        
    Returns:
        AgentState: Updated state with formatted output
    """
    request_id = state["request_id"]
    logger.info(f"[{request_id}] Formatting final output")
    
    try:
        # Calculate processing time
        processing_time = time.time() - state["start_time"]
        
        # Add final metadata
        state["metadata"].update({
            "processing_time_seconds": round(processing_time, 2),
            "final_word_count": state["word_count"],
            "total_retries": state["retry_count"],
            "quality_passed": state["validation_passed"],
            "platform_compliant": state["platform_compliant"],
            "hallucination_count": len(state["hallucination_markers"])
        })
        
        logger.info(f"[{request_id}] Output formatting completed in {processing_time:.2f}s")
        
    except Exception as e:
        logger.error(f"[{request_id}] Output formatting error: {e}")
        state["error_message"] = format_error_message(e, "Output formatting")
    
    return state

# Workflow routing functions

def should_retry(state: AgentState) -> str:
    """
    Determine if generation should be retried based on errors and retry count.
    
    Args:
        state (AgentState): Current workflow state
        
    Returns:
        str: Next node name or END
    """
    request_id = state["request_id"]
    retry_count = state["retry_count"]
    max_retries = state["max_retries"]
    
    # If no error, proceed to quality check
    if not state["error_message"]:
        return "quality_check"
    
    # If max retries reached, end with error
    if retry_count >= max_retries:
        logger.warning(f"[{request_id}] Max retries ({max_retries}) reached for generation errors")
        return END
    
    # Safety check to prevent infinite loops
    if retry_count > 10:  # Hard limit regardless of max_retries setting
        logger.error(f"[{request_id}] Hard retry limit reached ({retry_count}), ending workflow")
        return END
    
    # Retry content generation
    logger.info(f"[{request_id}] Retrying content generation (attempt {retry_count + 1})")
    return "generate_content"

def should_retry_quality(state: AgentState) -> str:
    """
    Determine if quality check failed and should retry.
    
    Args:
        state (AgentState): Current workflow state
        
    Returns:
        str: Next node name or END
    """
    request_id = state["request_id"]
    retry_count = state["retry_count"]
    max_retries = state["max_retries"]
    
    # If quality check passed, format output
    if state["validation_passed"]:
        return "format_output"
    
    # If max retries reached, end with current content
    if retry_count >= max_retries:    
        logger.warning(f"[{request_id}] Quality check failed but max retries ({max_retries}) reached")
        return "format_output"  # Still format output even if quality is poor
    
    # Safety check to prevent infinite loops  
    if retry_count > 10:  # Hard limit regardless of max_retries setting
        logger.error(f"[{request_id}] Hard retry limit reached ({retry_count}), formatting current output")
        return "format_output"
    
    # Increment retry count for quality-based retries
    state["retry_count"] += 1
    
    # Retry content generation
    logger.info(f"[{request_id}] Retrying due to quality issues (attempt {state['retry_count']})")
    return "generate_content"

def create_workflow():
    """
    Create and compile the LangGraph workflow.
    
    Returns:
        CompiledGraph: Compiled LangGraph workflow
        
    Raises:
        ImportError: If LangGraph dependencies are not available
    """
    if StateGraph is None:
        raise ImportError("LangGraph dependencies not available. Please install langgraph and langchain-openai")
    
    # Define the state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("validate_input", validate_input)
    workflow.add_node("build_context", build_context)  
    workflow.add_node("generate_content", generate_content)
    workflow.add_node("quality_check", quality_check)
    workflow.add_node("format_output", format_output)
    
    # Define workflow edges
    workflow.set_entry_point("validate_input")
    
    workflow.add_edge("validate_input", "build_context")
    workflow.add_edge("build_context", "generate_content")
    
    # Conditional edges for retry logic
    workflow.add_conditional_edges(
        "generate_content",
        should_retry,
        {
            "quality_check": "quality_check",
            "generate_content": "generate_content",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "quality_check",
        should_retry_quality,
        {
            "format_output": "format_output",
            "generate_content": "generate_content"
        }
    )
    
    workflow.add_edge("format_output", END)
    
    # Compile the workflow
    return workflow.compile()

def run_writing_agent(
    description: str,
    mood_values: Dict[str, int],
    platform: str,
    max_retries: int = 2
) -> Dict[str, Any]:
    """
    Main entry point for the AI Writing Assistant.
    
    This function executes the complete workflow for generating content
    based on user requirements with mood and platform specifications.
    
    Args:
        description (str): Content description/topic from user
        mood_values (Dict[str, int]): Mood intensity settings (0-10)
        platform (str): Target platform (twitter, linkedin, etc.)
        max_retries (int): Maximum retry attempts for failures
        
    Returns:
        Dict[str, Any]: Complete results including content, metadata, and status
        
    Raises:
        ConfigurationError: If configuration is invalid
        ImportError: If required dependencies are missing
    """
    request_id = create_request_id()
    start_time = time.time()
    
    logger.info(f"[{request_id}] Starting writing agent workflow")
    
    try:
        # Validate configuration
        config = get_config()
        if not config.OPENAI_API_KEY:
            raise ConfigurationError("OpenAI API key not configured")
        
        # Initialize state
        initial_state: AgentState = {
            "description": description,
            "mood_values": mood_values,
            "platform": platform,
            "system_prompt": "",
            "generated_content": "",
            "validation_passed": False,
            "retry_count": 0,
            "max_retries": max_retries,
            "error_message": "",
            "metadata": {
                "request_id": request_id,
                "model_name": config.MODEL_NAME,
                "max_tokens": config.MAX_TOKENS,
                "temperature": config.TEMPERATURE
            },
            "request_id": request_id,
            "start_time": start_time,
            "word_count": 0,
            "hallucination_markers": [],
            "platform_compliant": False
        }
        
        # Create and run workflow with increased recursion limit
        workflow = create_workflow()
        final_state = workflow.invoke(initial_state, {"recursion_limit": 50})
        
        # Prepare response
        success = final_state["validation_passed"] and not final_state["error_message"]
        
        response = {
            "success": success,
            "content": final_state["generated_content"],
            "word_count": final_state["word_count"],
            "platform_compliant": final_state["platform_compliant"],
            "error_message": final_state["error_message"],
            "metadata": final_state["metadata"],
            "request_id": request_id
        }
        
        if success:
            logger.info(f"[{request_id}] Workflow completed successfully")
        else:
            logger.error(f"[{request_id}] Workflow completed with errors: {final_state['error_message']}")
        
        return response
        
    except Exception as e:
        logger.error(f"[{request_id}] Workflow execution failed: {e}")
        return {
            "success": False,
            "content": "",
            "word_count": 0,
            "platform_compliant": False,
            "error_message": format_error_message(e, "Workflow execution"),
            "metadata": {"request_id": request_id, "execution_time": time.time() - start_time},
            "request_id": request_id
        }

# Async wrapper for potential future use
async def run_writing_agent_async(
    description: str,
    mood_values: Dict[str, int], 
    platform: str,
    max_retries: int = 2
) -> Dict[str, Any]:
    """
    Async version of run_writing_agent for concurrent execution.
    
    Args:
        description (str): Content description/topic
        mood_values (Dict[str, int]): Mood settings
        platform (str): Target platform
        max_retries (int): Maximum retry attempts
        
    Returns:
        Dict[str, Any]: Generation results
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, 
        run_writing_agent,
        description,
        mood_values,
        platform,
        max_retries
    )