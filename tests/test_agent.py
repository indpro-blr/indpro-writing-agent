"""
Unit tests for the LangGraph agent workflow.

This module tests all aspects of the agent workflow including:
- State validation and processing
- Node functions and their logic
- Workflow routing and retry mechanisms
- Error handling and recovery
"""

import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import modules under test
try:
    from api.agent import (
        AgentState,
        validate_input,
        build_context,
        generate_content,
        quality_check,
        format_output,
        should_retry,
        should_retry_quality,
        create_workflow,
        run_writing_agent
    )
    from api.config import Config
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    pytest.skip("API modules not available", allow_module_level=True)

# Load test fixtures
def load_test_fixtures():
    """Load test data from fixtures file."""
    fixtures_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'sample_inputs.json')
    with open(fixtures_path, 'r') as f:
        return json.load(f)

@pytest.fixture
def test_fixtures():
    """Provide test fixtures as a pytest fixture."""
    return load_test_fixtures()

@pytest.fixture
def sample_state():
    """Create a sample agent state for testing."""
    return {
        'description': 'Write about the benefits of remote work',
        'mood_values': {
            'professional': 7,
            'confident': 6,
            'enthusiastic': 4,
            'empathetic': 3,
            'creative': 4,
            'urgent': 2,
            'friendly': 5,
            'authoritative': 5,
            'humorous': 2,
            'inspiring': 4
        },
        'platform': 'linkedin',
        'system_prompt': '',
        'generated_content': '',
        'validation_passed': False,
        'retry_count': 0,
        'max_retries': 2,
        'error_message': '',
        'metadata': {},
        'request_id': 'test_request_123',
        'start_time': 1234567890.0,
        'word_count': 0,
        'hallucination_markers': [],
        'platform_compliant': False
    }

class TestValidateInput:
    """Test cases for the validate_input node function."""
    
    @pytest.mark.unit
    def test_valid_input(self, sample_state):
        """Test validation with valid input parameters."""
        result = validate_input(sample_state)
        
        assert result['validation_passed'] is True
        assert result['error_message'] == ''
        assert result['metadata']['validation_status'] == 'passed'
        assert len(result['description']) >= 10
    
    @pytest.mark.unit
    def test_empty_description(self, sample_state):
        """Test validation fails with empty description."""
        sample_state['description'] = ''
        result = validate_input(sample_state)
        
        assert result['validation_passed'] is False
        assert 'at least 10 characters' in result['error_message']
    
    @pytest.mark.unit
    def test_short_description(self, sample_state):
        """Test validation fails with too short description."""
        sample_state['description'] = 'Hi there'
        result = validate_input(sample_state)
        
        assert result['validation_passed'] is False
        assert 'at least 10 characters' in result['error_message']
    
    @pytest.mark.unit
    def test_long_description(self, sample_state):
        """Test validation fails with too long description."""
        sample_state['description'] = 'A' * 2001
        result = validate_input(sample_state)
        
        assert result['validation_passed'] is False
        assert 'less than 2000 characters' in result['error_message']
    
    @pytest.mark.unit
    def test_invalid_platform(self, sample_state):
        """Test validation fails with invalid platform."""
        sample_state['platform'] = 'invalid_platform'
        result = validate_input(sample_state)
        
        assert result['validation_passed'] is False
        assert 'Invalid platform' in result['error_message']
    
    @pytest.mark.unit
    def test_invalid_mood_values(self, sample_state):
        """Test validation fails with invalid mood values."""
        sample_state['mood_values'] = {'professional': 15}  # Out of range
        result = validate_input(sample_state)
        
        assert result['validation_passed'] is False
        assert 'between 0-10' in result['error_message']
    
    @pytest.mark.unit
    def test_mood_values_not_dict(self, sample_state):
        """Test validation fails when mood_values is not a dictionary."""
        sample_state['mood_values'] = "not a dict"
        result = validate_input(sample_state)
        
        assert result['validation_passed'] is False
        assert 'must be a dictionary' in result['error_message']

class TestBuildContext:
    """Test cases for the build_context node function."""
    
    @pytest.mark.unit
    def test_successful_context_building(self, sample_state):
        """Test successful system prompt generation."""
        # First validate input
        validated_state = validate_input(sample_state)
        
        # Then build context
        result = build_context(validated_state)
        
        assert result['system_prompt'] != ''
        assert 'linkedin' in result['system_prompt'].lower()
        assert result['metadata']['prompt_length'] > 0
    
    @pytest.mark.unit
    def test_context_building_with_invalid_data(self, sample_state):
        """Test context building handles invalid data gracefully."""
        sample_state['description'] = ''
        sample_state['platform'] = 'invalid'
        
        result = build_context(sample_state)
        
        assert result['error_message'] != ''

class TestGenerateContent:
    """Test cases for the generate_content node function."""
    
    @pytest.mark.unit
    @patch('api.agent.ChatOpenAI')
    @patch('api.agent.get_config')
    def test_successful_generation(self, mock_config, mock_openai, sample_state):
        """Test successful content generation with mocked OpenAI."""
        # Mock configuration
        mock_config.return_value = Mock(
            OPENAI_API_KEY='test-key',
            MODEL_NAME='gpt-4-turbo-preview',
            MAX_TOKENS=500,
            TEMPERATURE=0.7,
            TOP_P=0.9,
            TIMEOUT=30
        )
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.content = "This is generated content about remote work benefits."
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_openai.return_value = mock_llm
        
        # Build context first
        sample_state['system_prompt'] = "Generate content about remote work"
        
        result = generate_content(sample_state)
        
        assert result['generated_content'] != ''
        assert result['word_count'] > 0
        assert result['metadata']['generation_successful'] is True
        mock_llm.invoke.assert_called_once()
    
    @pytest.mark.unit
    @patch('api.agent.ChatOpenAI')  
    @patch('api.agent.get_config')
    def test_generation_failure(self, mock_config, mock_openai, sample_state):
        """Test handling of OpenAI API failures."""
        # Mock configuration
        mock_config.return_value = Mock(OPENAI_API_KEY='test-key')
        
        # Mock OpenAI to raise an exception
        mock_openai.side_effect = Exception("API Error")
        
        result = generate_content(sample_state)
        
        assert result['error_message'] != ''
        assert result['metadata']['generation_successful'] is False
        assert result['retry_count'] == 1
    
    @pytest.mark.unit
    @patch('api.agent.ChatOpenAI')
    @patch('api.agent.get_config')
    def test_empty_response_handling(self, mock_config, mock_openai, sample_state):
        """Test handling of empty responses from OpenAI."""
        # Mock configuration
        mock_config.return_value = Mock(OPENAI_API_KEY='test-key')
        
        # Mock empty response
        mock_response = Mock()
        mock_response.content = ""
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_openai.return_value = mock_llm
        
        sample_state['system_prompt'] = "Generate content"
        
        result = generate_content(sample_state)
        
        assert 'empty' in result['error_message'].lower()
        assert result['retry_count'] == 1

class TestQualityCheck:
    """Test cases for the quality_check node function."""
    
    @pytest.mark.unit
    def test_quality_check_passes(self, sample_state):
        """Test quality check with good content."""
        sample_state['generated_content'] = "This is excellent content about remote work productivity and work-life balance. It provides valuable insights for professionals."
        sample_state['platform'] = 'linkedin'
        sample_state['word_count'] = 20
        
        result = quality_check(sample_state)
        
        assert result['validation_passed'] is True
        assert result['platform_compliant'] is True
        assert len(result['hallucination_markers']) == 0
    
    @pytest.mark.unit
    def test_quality_check_detects_hallucinations(self, sample_state):
        """Test quality check detects hallucination markers."""
        sample_state['generated_content'] = "As an AI, I can't provide specific advice about remote work."
        
        result = quality_check(sample_state)
        
        assert result['validation_passed'] is False
        assert len(result['hallucination_markers']) > 0
        assert 'hallucination markers' in result['error_message']
    
    @pytest.mark.unit
    def test_quality_check_word_count_validation(self, sample_state):
        """Test quality check validates word count for platform."""
        sample_state['generated_content'] = "Too short"
        sample_state['platform'] = 'linkedin'  # Requires 10-300 words
        sample_state['word_count'] = 2
        
        result = quality_check(sample_state)
        
        assert result['validation_passed'] is False
        assert result['platform_compliant'] is False
        assert 'word count' in result['error_message'].lower()
    
    @pytest.mark.unit
    def test_quality_check_very_short_content(self, sample_state):
        """Test quality check fails for very short content."""
        sample_state['generated_content'] = "Hi"
        sample_state['word_count'] = 1
        
        result = quality_check(sample_state)
        
        assert result['validation_passed'] is False
        assert 'too short' in result['error_message']

class TestFormatOutput:
    """Test cases for the format_output node function."""
    
    @pytest.mark.unit
    def test_format_output_success(self, sample_state):
        """Test successful output formatting."""
        sample_state['start_time'] = 1234567890.0
        sample_state['word_count'] = 50
        sample_state['retry_count'] = 1
        sample_state['validation_passed'] = True
        sample_state['platform_compliant'] = True
        sample_state['hallucination_markers'] = []
        
        with patch('time.time', return_value=1234567892.5):  # 2.5 seconds later
            result = format_output(sample_state)
        
        metadata = result['metadata']
        assert metadata['processing_time_seconds'] == 2.5
        assert metadata['final_word_count'] == 50
        assert metadata['total_retries'] == 1
        assert metadata['quality_passed'] is True
        assert metadata['platform_compliant'] is True
        assert metadata['hallucination_count'] == 0

class TestWorkflowRouting:
    """Test cases for workflow routing functions."""
    
    @pytest.mark.unit
    def test_should_retry_no_error(self, sample_state):
        """Test routing when there's no error."""
        sample_state['error_message'] = ''
        
        result = should_retry(sample_state)
        
        assert result == 'quality_check'
    
    @pytest.mark.unit
    def test_should_retry_max_retries_reached(self, sample_state):
        """Test routing when max retries reached."""
        sample_state['error_message'] = 'Some error'
        sample_state['retry_count'] = 2
        sample_state['max_retries'] = 2
        
        result = should_retry(sample_state)
        
        assert result == 'END'
    
    @pytest.mark.unit
    def test_should_retry_content_generation(self, sample_state):
        """Test routing to retry content generation."""
        sample_state['error_message'] = 'Some error'
        sample_state['retry_count'] = 1
        sample_state['max_retries'] = 2
        
        result = should_retry(sample_state)
        
        assert result == 'generate_content'
    
    @pytest.mark.unit
    def test_should_retry_quality_passed(self, sample_state):
        """Test quality routing when validation passed."""
        sample_state['validation_passed'] = True
        
        result = should_retry_quality(sample_state)
        
        assert result == 'format_output'
    
    @pytest.mark.unit
    def test_should_retry_quality_failed_max_retries(self, sample_state):
        """Test quality routing when validation failed but max retries reached."""
        sample_state['validation_passed'] = False
        sample_state['retry_count'] = 2
        sample_state['max_retries'] = 2
        
        result = should_retry_quality(sample_state)
        
        assert result == 'format_output'

class TestWorkflowIntegration:
    """Integration tests for the complete workflow."""
    
    @pytest.mark.integration
    @patch('api.agent.ChatOpenAI')
    @patch('api.agent.get_config')
    def test_successful_workflow_execution(self, mock_config, mock_openai):
        """Test complete workflow execution with mocked dependencies."""
        # Mock configuration
        mock_config.return_value = Mock(
            OPENAI_API_KEY='test-key',
            MODEL_NAME='gpt-4-turbo-preview',
            MAX_TOKENS=500,
            TEMPERATURE=0.7,
            TOP_P=0.9,
            TIMEOUT=30
        )
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.content = "Remote work offers significant benefits for productivity and work-life balance. It allows employees to work in comfortable environments while reducing commute stress."
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_openai.return_value = mock_llm
        
        # Test data
        description = "Write about the benefits of remote work"
        mood_values = {
            'professional': 7, 'confident': 6, 'enthusiastic': 4,
            'empathetic': 3, 'creative': 4, 'urgent': 2,
            'friendly': 5, 'authoritative': 5, 'humorous': 2, 'inspiring': 4
        }
        platform = 'linkedin'
        
        # Execute workflow
        result = run_writing_agent(description, mood_values, platform)
        
        assert result['success'] is True
        assert result['content'] != ''
        assert result['word_count'] > 0
        assert result['error_message'] == ''
        assert 'request_id' in result
    
    @pytest.mark.integration
    @patch('api.agent.get_config')
    def test_workflow_with_missing_api_key(self, mock_config):
        """Test workflow fails gracefully with missing API key."""
        # Mock configuration without API key
        mock_config.return_value = Mock(OPENAI_API_KEY='')
        
        description = "Write about remote work"
        mood_values = {'professional': 7}
        platform = 'linkedin'
        
        result = run_writing_agent(description, mood_values, platform)
        
        assert result['success'] is False
        assert 'api key' in result['error_message'].lower()
    
    @pytest.mark.integration
    def test_workflow_with_invalid_inputs(self):
        """Test workflow handles invalid inputs gracefully."""
        description = ""  # Invalid: too short
        mood_values = {'professional': 15}  # Invalid: out of range
        platform = 'invalid_platform'  # Invalid platform
        
        result = run_writing_agent(description, mood_values, platform)
        
        assert result['success'] is False
        assert result['error_message'] != ''

@pytest.mark.unit
def test_create_workflow():
    """Test workflow creation and compilation."""
    try:
        workflow = create_workflow()
        assert workflow is not None
        # Test that workflow has the expected structure
        assert hasattr(workflow, 'invoke')
    except ImportError:
        # Expected if LangGraph is not available
        pytest.skip("LangGraph not available for workflow creation test")

class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.unit
    def test_workflow_handles_unexpected_errors(self, sample_state):
        """Test workflow handles unexpected errors gracefully."""
        # Simulate an unexpected error in state processing
        with patch('api.agent.validate_input', side_effect=RuntimeError("Unexpected error")):
            description = "Test description for error handling"
            mood_values = {'professional': 5}
            platform = 'twitter'
            
            result = run_writing_agent(description, mood_values, platform)
            
            assert result['success'] is False
            assert 'error' in result['error_message'].lower()
            assert result['request_id'] is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])