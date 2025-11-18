"""
Unit tests for the prompt engineering module.

This module tests prompt generation, mood combinations, platform specifications,
and anti-hallucination strategies.
"""

import pytest
import json
from unittest.mock import patch

# Import modules under test
try:
    from api.prompts import (
        MOOD_DEFINITIONS,
        PLATFORM_SPECS,
        get_mood_instruction,
        build_mood_combination_prompt,
        build_anti_hallucination_prompt,
        validate_prompt_length,
        get_platform_word_limit,
        get_available_moods,
        get_available_platforms,
        create_mood_summary,
        validate_mood_combination
    )
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    pytest.skip("API modules not available", allow_module_level=True)

class TestMoodInstructions:
    """Test cases for mood instruction generation."""
    
    @pytest.mark.unit
    def test_get_mood_instruction_valid(self):
        """Test getting mood instruction with valid parameters."""
        instruction = get_mood_instruction("professional", 5)
        
        assert isinstance(instruction, str)
        assert len(instruction) > 0
        assert "professional" in instruction.lower()
    
    @pytest.mark.unit
    def test_get_mood_instruction_all_intensities(self):
        """Test all intensity levels for a mood."""
        for intensity in range(11):  # 0-10
            instruction = get_mood_instruction("professional", intensity)
            assert isinstance(instruction, str)
            assert len(instruction) > 0
    
    @pytest.mark.unit
    def test_get_mood_instruction_all_moods(self):
        """Test all available moods."""
        for mood in MOOD_DEFINITIONS.keys():
            instruction = get_mood_instruction(mood, 5)
            assert isinstance(instruction, str)
            assert len(instruction) > 0
    
    @pytest.mark.unit
    def test_get_mood_instruction_invalid_mood(self):
        """Test error handling for invalid mood."""
        with pytest.raises(ValueError, match="Unknown mood"):
            get_mood_instruction("invalid_mood", 5)
    
    @pytest.mark.unit
    def test_get_mood_instruction_invalid_intensity(self):
        """Test error handling for invalid intensity."""
        with pytest.raises(ValueError, match="Intensity must be between 0-10"):
            get_mood_instruction("professional", 15)
        
        with pytest.raises(ValueError, match="Intensity must be between 0-10"):
            get_mood_instruction("professional", -1)

class TestMoodCombinations:
    """Test cases for mood combination prompts."""
    
    @pytest.mark.unit
    def test_build_mood_combination_empty(self):
        """Test mood combination with empty values."""
        result = build_mood_combination_prompt({})
        
        assert "neutral, balanced tone" in result
    
    @pytest.mark.unit
    def test_build_mood_combination_all_zero(self):
        """Test mood combination with all zero values."""
        mood_values = {mood: 0 for mood in MOOD_DEFINITIONS.keys()}
        result = build_mood_combination_prompt(mood_values)
        
        assert "neutral, balanced tone" in result
    
    @pytest.mark.unit
    def test_build_mood_combination_single_mood(self):
        """Test mood combination with single active mood."""
        mood_values = {"professional": 8}
        result = build_mood_combination_prompt(mood_values)
        
        assert "Professional (Level 8)" in result
        assert "TONE AND STYLE REQUIREMENTS" in result
    
    @pytest.mark.unit
    def test_build_mood_combination_multiple_moods(self):
        """Test mood combination with multiple active moods."""
        mood_values = {
            "professional": 7,
            "confident": 6,
            "enthusiastic": 4,
            "empathetic": 0,
            "creative": 2
        }
        result = build_mood_combination_prompt(mood_values)
        
        assert "Professional (Level 7)" in result
        assert "Confident (Level 6)" in result
        assert "Enthusiastic (Level 4)" in result
        assert "Creative (Level 2)" in result
        assert "Empathetic" not in result  # Should not include zero values
    
    @pytest.mark.unit
    def test_build_mood_combination_invalid_input(self):
        """Test mood combination with invalid input."""
        result = build_mood_combination_prompt("not a dict")
        
        assert "neutral, balanced tone" in result
    
    @pytest.mark.unit
    def test_build_mood_combination_with_warnings(self):
        """Test mood combination generates warnings for conflicts."""
        mood_values = {"professional": 10, "humorous": 10}
        
        with patch('api.prompts.logger') as mock_logger:
            result = build_mood_combination_prompt(mood_values)
            
            assert isinstance(result, str)
            assert len(result) > 0

class TestPlatformSpecs:
    """Test cases for platform specifications."""
    
    @pytest.mark.unit
    def test_get_platform_word_limit_valid(self):
        """Test getting word limits for valid platforms."""
        for platform in PLATFORM_SPECS.keys():
            limits = get_platform_word_limit(platform)
            
            assert isinstance(limits, dict)
            assert 'min' in limits
            assert 'max' in limits
            assert limits['min'] >= 0
            assert limits['max'] > limits['min']
    
    @pytest.mark.unit
    def test_get_platform_word_limit_invalid(self):
        """Test error handling for invalid platform."""
        with pytest.raises(ValueError, match="Unknown platform"):
            get_platform_word_limit("invalid_platform")
    
    @pytest.mark.unit
    def test_platform_specs_completeness(self):
        """Test that all platforms have required specifications."""
        required_keys = ['word_range', 'tone', 'features', 'format', 'audience', 'style_notes']
        
        for platform, specs in PLATFORM_SPECS.items():
            for key in required_keys:
                assert key in specs, f"Platform {platform} missing {key}"
            
            # Test word range format
            word_range = specs['word_range']
            assert isinstance(word_range, dict)
            assert 'min' in word_range
            assert 'max' in word_range

class TestAntiHallucinationPrompts:
    """Test cases for anti-hallucination prompt generation."""
    
    @pytest.mark.unit
    def test_build_anti_hallucination_prompt_valid(self):
        """Test building anti-hallucination prompt with valid inputs."""
        description = "Write about remote work benefits"
        mood_values = {"professional": 7, "confident": 5}
        platform = "linkedin"
        
        prompt = build_anti_hallucination_prompt(description, mood_values, platform)
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert description in prompt
        assert platform.upper() in prompt
        assert "NEVER mention that you are an AI" in prompt
        assert "CRITICAL REQUIREMENTS" in prompt
    
    @pytest.mark.unit
    def test_build_anti_hallucination_prompt_empty_description(self):
        """Test error handling for empty description."""
        with pytest.raises(ValueError, match="Description cannot be empty"):
            build_anti_hallucination_prompt("", {"professional": 5}, "twitter")
    
    @pytest.mark.unit
    def test_build_anti_hallucination_prompt_invalid_platform(self):
        """Test error handling for invalid platform."""
        with pytest.raises(ValueError, match="Unknown platform"):
            build_anti_hallucination_prompt(
                "Valid description", 
                {"professional": 5}, 
                "invalid_platform"
            )
    
    @pytest.mark.unit
    def test_anti_hallucination_prompt_contains_restrictions(self):
        """Test that prompt contains key anti-hallucination restrictions."""
        prompt = build_anti_hallucination_prompt(
            "Test description", 
            {"professional": 5}, 
            "twitter"
        )
        
        restrictions = [
            "NEVER mention that you are an AI",
            "NEVER use phrases like \"as an AI\"",
            "Don't ask questions back to the user",
            "Don't offer to help with other tasks",
            "Don't explain what you're doing"
        ]
        
        for restriction in restrictions:
            assert restriction in prompt

class TestPromptValidation:
    """Test cases for prompt validation functions."""
    
    @pytest.mark.unit
    def test_validate_prompt_length_valid(self):
        """Test prompt length validation with valid length."""
        short_prompt = "This is a short prompt for testing."
        
        assert validate_prompt_length(short_prompt, max_tokens=1000) is True
    
    @pytest.mark.unit
    def test_validate_prompt_length_too_long(self):
        """Test prompt length validation with excessive length."""
        long_prompt = "A" * 5000  # Very long prompt
        
        with patch('api.prompts.logger') as mock_logger:
            result = validate_prompt_length(long_prompt, max_tokens=100)
            
            assert result is False
    
    @pytest.mark.unit
    def test_validate_prompt_length_empty(self):
        """Test prompt length validation with empty prompt."""
        assert validate_prompt_length("", max_tokens=1000) is True

class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    @pytest.mark.unit
    def test_get_available_moods(self):
        """Test getting list of available moods."""
        moods = get_available_moods()
        
        assert isinstance(moods, list)
        assert len(moods) > 0
        assert all(mood in MOOD_DEFINITIONS for mood in moods)
    
    @pytest.mark.unit
    def test_get_available_platforms(self):
        """Test getting list of available platforms."""
        platforms = get_available_platforms()
        
        assert isinstance(platforms, list)
        assert len(platforms) > 0
        assert all(platform in PLATFORM_SPECS for platform in platforms)
    
    @pytest.mark.unit
    def test_create_mood_summary_empty(self):
        """Test mood summary with empty input."""
        summary = create_mood_summary({})
        
        assert "No specific mood settings" in summary
    
    @pytest.mark.unit
    def test_create_mood_summary_all_zero(self):
        """Test mood summary with all zero values."""
        mood_values = {mood: 0 for mood in MOOD_DEFINITIONS.keys()}
        summary = create_mood_summary(mood_values)
        
        assert "No active moods" in summary
    
    @pytest.mark.unit
    def test_create_mood_summary_with_active_moods(self):
        """Test mood summary with active moods."""
        mood_values = {
            "professional": 8,
            "confident": 6,
            "creative": 4,
            "empathetic": 0
        }
        summary = create_mood_summary(mood_values)
        
        assert "Active moods:" in summary
        assert "Professional (Very High - 8/10)" in summary
        assert "Confident (High - 6/10)" in summary
        assert "Creative (Moderate - 4/10)" in summary
        assert "Empathetic" not in summary

class TestMoodValidation:
    """Test cases for mood validation functions."""
    
    @pytest.mark.unit
    def test_validate_mood_combination_no_conflicts(self):
        """Test mood validation with no conflicts."""
        mood_values = {
            "professional": 5,
            "confident": 4,
            "friendly": 6
        }
        warnings = validate_mood_combination(mood_values)
        
        assert isinstance(warnings, list)
        # Should have no warnings for moderate values
    
    @pytest.mark.unit
    def test_validate_mood_combination_conflicts(self):
        """Test mood validation detects conflicts."""
        mood_values = {
            "professional": 9,
            "humorous": 9
        }
        warnings = validate_mood_combination(mood_values)
        
        assert isinstance(warnings, list)
        assert any("professional and humorous" in warning.lower() for warning in warnings)
    
    @pytest.mark.unit
    def test_validate_mood_combination_too_many_high(self):
        """Test mood validation detects too many high-intensity moods."""
        mood_values = {
            "professional": 8,
            "confident": 8,
            "authoritative": 8,
            "urgent": 8,
            "creative": 8
        }
        warnings = validate_mood_combination(mood_values)
        
        assert isinstance(warnings, list)
        assert any("too many high-intensity" in warning.lower() for warning in warnings)

class TestEdgeCases:
    """Test cases for edge cases and error conditions."""
    
    @pytest.mark.unit
    def test_mood_definitions_completeness(self):
        """Test that all moods have complete intensity definitions."""
        for mood, definitions in MOOD_DEFINITIONS.items():
            for intensity in range(11):  # 0-10
                assert intensity in definitions, f"Mood {mood} missing intensity {intensity}"
                assert isinstance(definitions[intensity], str)
                assert len(definitions[intensity]) > 0
    
    @pytest.mark.unit
    def test_platform_specs_consistency(self):
        """Test platform specifications are consistent."""
        for platform, specs in PLATFORM_SPECS.items():
            word_range = specs['word_range']
            
            # Min should be less than max
            assert word_range['min'] < word_range['max']
            
            # Min should be positive
            assert word_range['min'] >= 0
            
            # Character limit should be reasonable if specified
            if specs.get('character_limit'):
                assert specs['character_limit'] > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])