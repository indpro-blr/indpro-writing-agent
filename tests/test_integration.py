"""
Integration tests for the AI Writing Assistant.

This module provides end-to-end testing of the complete system,
including API integration, workflow execution, and error handling.
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock

# Import modules under test
try:
    from api import run_writing_agent
    from api.config import Config
    from api.prompts import get_available_platforms, get_available_moods
    from api.utils import count_words, validate_word_count
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    pytest.skip("API modules not available", allow_module_level=True)

class TestFullWorkflowIntegration:
    """Integration tests for complete workflow execution."""
    
    @pytest.mark.integration
    @patch('api.agent.ChatOpenAI')
    @patch('api.config.get_config')
    def test_complete_workflow_success(self, mock_config, mock_openai):
        """Test complete workflow from input to output."""
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
        mock_response.content = "Remote work has revolutionized how we approach productivity and work-life balance. Companies embracing flexible work arrangements report higher employee satisfaction and retention rates."
        
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_openai.return_value = mock_llm
        
        # Test inputs
        description = "Write about the benefits of remote work for modern businesses"
        mood_values = {
            'professional': 8,
            'confident': 7,
            'enthusiastic': 4,
            'empathetic': 3,
            'creative': 4,
            'urgent': 2,
            'friendly': 4,
            'authoritative': 6,
            'humorous': 2,
            'inspiring': 5
        }
        platform = 'linkedin'
        
        # Execute workflow
        result = run_writing_agent(description, mood_values, platform, max_retries=1)
        
        # Assertions
        assert result['success'] is True
        assert result['content'] != ''
        assert result['word_count'] > 0
        assert result['platform_compliant'] is True
        assert result['error_message'] == ''
        assert 'request_id' in result
        assert 'metadata' in result
        
        # Verify OpenAI was called
        mock_llm.invoke.assert_called_once()
        
        # Verify content quality
        assert len(result['content']) > 50
        assert 'remote work' in result['content'].lower()
    
    @pytest.mark.integration
    def test_workflow_with_all_platforms(self):
        """Test workflow execution with all supported platforms."""
        description = "Write about sustainable living practices"
        mood_values = {'professional': 5, 'friendly': 6, 'inspiring': 7}
        
        platforms = get_available_platforms()
        
        with patch('api.agent.ChatOpenAI') as mock_openai:
            with patch('api.config.get_config') as mock_config:
                # Setup mocks
                mock_config.return_value = Mock(
                    OPENAI_API_KEY='test-key',
                    MODEL_NAME='gpt-4-turbo-preview'
                )
                
                mock_response = Mock()
                mock_response.content = "Sustainable living starts with small changes that make a big impact on our environment."
                
                mock_llm = Mock()
                mock_llm.invoke.return_value = mock_response
                mock_openai.return_value = mock_llm
                
                # Test each platform
                for platform in platforms:
                    result = run_writing_agent(description, mood_values, platform)
                    
                    assert result['success'] is True
                    assert result['content'] != ''
                    assert isinstance(result['word_count'], int)
    
    @pytest.mark.integration
    def test_workflow_with_extreme_mood_combinations(self):
        """Test workflow with extreme mood value combinations."""
        description = "Write about artificial intelligence in healthcare"
        platform = 'blog'
        
        test_cases = [
            # All maximum values
            {mood: 10 for mood in get_available_moods()},
            # All minimum values
            {mood: 0 for mood in get_available_moods()},
            # Mixed extreme values
            {
                'professional': 10,
                'humorous': 10,
                'urgent': 0,
                'creative': 10,
                'empathetic': 0
            }
        ]
        
        with patch('api.agent.ChatOpenAI') as mock_openai:
            with patch('api.config.get_config') as mock_config:
                # Setup mocks
                mock_config.return_value = Mock(OPENAI_API_KEY='test-key')
                mock_response = Mock()
                mock_response.content = "AI in healthcare represents a significant advancement in medical technology."
                mock_llm = Mock()
                mock_llm.invoke.return_value = mock_response
                mock_openai.return_value = mock_llm
                
                for mood_values in test_cases:
                    result = run_writing_agent(description, mood_values, platform)
                    
                    # Should succeed despite extreme combinations
                    assert result['success'] is True
                    assert result['content'] != ''

class TestErrorHandlingIntegration:
    """Integration tests for error handling scenarios."""
    
    @pytest.mark.integration
    @patch('api.config.get_config')
    def test_missing_api_key_error(self, mock_config):
        """Test handling of missing OpenAI API key."""
        mock_config.return_value = Mock(OPENAI_API_KEY='')
        
        result = run_writing_agent(
            "Test description",
            {'professional': 5},
            'twitter'
        )
        
        assert result['success'] is False
        assert 'api key' in result['error_message'].lower()
    
    @pytest.mark.integration
    @patch('api.agent.ChatOpenAI')
    @patch('api.config.get_config')
    def test_api_timeout_handling(self, mock_config, mock_openai):
        """Test handling of API timeout errors."""
        mock_config.return_value = Mock(OPENAI_API_KEY='test-key')
        
        # Mock timeout error
        mock_openai.side_effect = TimeoutError("Request timed out")
        
        result = run_writing_agent(
            "Test description for timeout",
            {'professional': 5},
            'twitter',
            max_retries=1
        )
        
        assert result['success'] is False
        assert 'timeout' in result['error_message'].lower() or 'error' in result['error_message'].lower()
    
    @pytest.mark.integration
    @patch('api.agent.ChatOpenAI')
    @patch('api.config.get_config') 
    def test_api_rate_limit_handling(self, mock_config, mock_openai):
        """Test handling of API rate limit errors."""
        mock_config.return_value = Mock(OPENAI_API_KEY='test-key')
        
        # Mock rate limit error
        mock_openai.side_effect = Exception("Rate limit exceeded")
        
        result = run_writing_agent(
            "Test description for rate limit",
            {'professional': 5},
            'twitter',
            max_retries=1
        )
        
        assert result['success'] is False
        assert result['error_message'] != ''
    
    @pytest.mark.integration
    def test_invalid_input_combinations(self):
        """Test various invalid input combinations."""
        invalid_cases = [
            # Empty description
            ("", {'professional': 5}, 'twitter'),
            # Invalid platform
            ("Valid description", {'professional': 5}, 'invalid_platform'),
            # Invalid mood values
            ("Valid description", {'professional': 15}, 'twitter'),
            # Non-dict mood values
            ("Valid description", "not a dict", 'twitter'),
        ]
        
        for description, mood_values, platform in invalid_cases:
            result = run_writing_agent(description, mood_values, platform)
            
            assert result['success'] is False
            assert result['error_message'] != ''
            assert result['content'] == ''

class TestContentQualityIntegration:
    """Integration tests for content quality validation."""
    
    @pytest.mark.integration
    @patch('api.agent.ChatOpenAI')
    @patch('api.config.get_config')
    def test_content_quality_validation(self, mock_config, mock_openai):
        """Test that generated content passes quality checks."""
        mock_config.return_value = Mock(OPENAI_API_KEY='test-key')
        
        # Mock high-quality response
        mock_response = Mock()
        mock_response.content = "Effective project management requires clear communication, realistic timelines, and adaptive strategies. Teams that embrace these principles consistently deliver successful outcomes."
        
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_openai.return_value = mock_llm
        
        result = run_writing_agent(
            "Write about effective project management strategies",
            {'professional': 7, 'authoritative': 6, 'confident': 8},
            'linkedin'
        )
        
        assert result['success'] is True
        assert result['platform_compliant'] is True
        assert result['word_count'] >= 10  # Minimum reasonable length
        
        # Check for absence of hallucination markers
        content_lower = result['content'].lower()
        hallucination_markers = ['as an ai', "i can't", "i don't have access"]
        for marker in hallucination_markers:
            assert marker not in content_lower
    
    @pytest.mark.integration
    @patch('api.agent.ChatOpenAI')
    @patch('api.config.get_config')
    def test_platform_word_count_compliance(self, mock_config, mock_openai):
        """Test that generated content complies with platform word limits."""
        mock_config.return_value = Mock(OPENAI_API_KEY='test-key')
        
        # Test different platforms with appropriate content lengths
        platform_tests = [
            ('twitter', "Great insights on productivity! #productivity #tips"),
            ('linkedin', "Professional development requires continuous learning and adaptation. In today's rapidly evolving business landscape, professionals must stay current with industry trends, develop new skills, and build meaningful networks. Organizations that invest in employee development see higher retention rates and improved performance outcomes."),
            ('blog', "The future of remote work continues to evolve as organizations adapt to changing workplace dynamics. Companies are discovering that flexible work arrangements not only improve employee satisfaction but also expand their talent pool beyond geographical limitations. This shift requires new approaches to team collaboration, performance management, and company culture development.")
        ]
        
        for platform, sample_content in platform_tests:
            mock_response = Mock()
            mock_response.content = sample_content
            mock_llm = Mock()
            mock_llm.invoke.return_value = mock_response
            mock_openai.return_value = mock_llm
            
            result = run_writing_agent(
                f"Write about remote work for {platform}",
                {'professional': 6, 'informative': 7},
                platform
            )
            
            assert result['success'] is True
            assert result['platform_compliant'] is True
            
            # Verify word count is within platform limits
            word_count = result['word_count']
            assert validate_word_count(result['content'], platform)

class TestRetryMechanismIntegration:
    """Integration tests for retry mechanisms."""
    
    @pytest.mark.integration
    @patch('api.agent.ChatOpenAI')
    @patch('api.config.get_config')
    def test_retry_on_api_failure(self, mock_config, mock_openai):
        """Test retry mechanism when API calls fail."""
        mock_config.return_value = Mock(OPENAI_API_KEY='test-key')
        
        # Mock first call fails, second succeeds
        mock_response = Mock()
        mock_response.content = "Successful content about innovation in technology."
        mock_llm = Mock()
        mock_llm.invoke.side_effect = [
            Exception("API Error"),  # First call fails
            mock_response  # Second call succeeds
        ]
        mock_openai.return_value = mock_llm
        
        result = run_writing_agent(
            "Write about innovation in technology",
            {'professional': 6, 'enthusiastic': 7},
            'blog',
            max_retries=2
        )
        
        assert result['success'] is True
        assert result['content'] != ''
        assert result['metadata']['total_retries'] == 1
        
        # Verify retry was attempted
        assert mock_llm.invoke.call_count == 2
    
    @pytest.mark.integration
    @patch('api.agent.ChatOpenAI')
    @patch('api.config.get_config')
    def test_max_retries_exceeded(self, mock_config, mock_openai):
        """Test behavior when max retries are exceeded."""
        mock_config.return_value = Mock(OPENAI_API_KEY='test-key')
        
        # Mock all calls fail
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("Persistent API Error")
        mock_openai.return_value = mock_llm
        
        result = run_writing_agent(
            "Test description",
            {'professional': 5},
            'twitter',
            max_retries=2
        )
        
        assert result['success'] is False
        assert 'error' in result['error_message'].lower()
        assert result['metadata']['total_retries'] == 2
        
        # Verify all retry attempts were made
        assert mock_llm.invoke.call_count == 2

class TestPerformanceIntegration:
    """Integration tests for performance characteristics."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    @patch('api.agent.ChatOpenAI')
    @patch('api.config.get_config')
    def test_workflow_performance(self, mock_config, mock_openai):
        """Test workflow performance and timing."""
        mock_config.return_value = Mock(OPENAI_API_KEY='test-key')
        
        mock_response = Mock()
        mock_response.content = "Performance test content about workflow efficiency."
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_openai.return_value = mock_llm
        
        start_time = time.time()
        
        result = run_writing_agent(
            "Write about workflow efficiency",
            {'professional': 6, 'efficient': 8},
            'email'
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert result['success'] is True
        assert execution_time < 10  # Should complete within 10 seconds (mocked)
        assert 'processing_time_seconds' in result['metadata']

class TestConfigurationIntegration:
    """Integration tests for configuration handling."""
    
    @pytest.mark.integration
    def test_configuration_loading(self):
        """Test that configuration loads properly."""
        try:
            config = Config()
            assert hasattr(config, 'OPENAI_API_KEY')
            assert hasattr(config, 'MODEL_NAME')
            assert hasattr(config, 'MAX_TOKENS')
        except Exception as e:
            # Expected if environment is not properly configured
            assert 'configuration' in str(e).lower() or 'api key' in str(e).lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])