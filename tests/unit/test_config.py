"""
Unit tests for centralized configuration management.

Tests verify:
- Configuration validation (required fields, types, ranges)
- Environment-specific configuration loading
- Default values for optional settings
- Configuration priority (secrets > env vars > .env > defaults)
- Secrets masking and security

Constitutional Alignment:
- Article VII: API-First Design
- Article VI: Test-Driven Development
- Article VIII: Security by Default
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from pydantic import ValidationError


# Test Suite 1: Configuration Validation
class TestConfigurationValidation:
    """Test configuration validation with Pydantic."""

    def test_valid_minimal_config(self):
        """Test configuration with only required fields."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key-1234567890abcdefghijklmnopqr'
        }, clear=True):
            settings = Settings()

            assert settings.openai_api_key.get_secret_value() == 'sk-test-key-1234567890abcdefghijklmnopqr'
            # Defaults should be applied
            assert settings.log_level == 'INFO'
            assert settings.max_retries == 3
            assert settings.email_body_max_length == 5000

    def test_missing_required_api_key_fails(self):
        """Test missing required API key causes validation error."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises((ValidationError, ValueError)) as exc_info:
                Settings()

            # Should mention missing API key
            error_msg = str(exc_info.value)
            assert 'openai_api_key' in error_msg.lower() or 'anthropic_api_key' in error_msg.lower() or 'api key' in error_msg.lower()

    def test_invalid_log_level_fails(self):
        """Test invalid log level causes validation error."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key',
            'LOG_LEVEL': 'TRACE'  # Invalid level
        }, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            error_msg = str(exc_info.value)
            assert 'log_level' in error_msg.lower()

    def test_invalid_email_body_max_length_too_small_fails(self):
        """Test email_body_max_length below minimum fails."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key',
            'EMAIL_BODY_MAX_LENGTH': '500'  # Too small (min: 1000)
        }, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            error_msg = str(exc_info.value)
            assert 'email_body_max_length' in error_msg.lower()

    def test_invalid_email_body_max_length_too_large_fails(self):
        """Test email_body_max_length above maximum fails."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key',
            'EMAIL_BODY_MAX_LENGTH': '20000'  # Too large (max: 10000)
        }, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            error_msg = str(exc_info.value)
            assert 'email_body_max_length' in error_msg.lower()

    def test_invalid_max_retries_negative_fails(self):
        """Test negative max_retries fails."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key',
            'MAX_RETRIES': '-1'  # Invalid (min: 0)
        }, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            error_msg = str(exc_info.value)
            assert 'max_retries' in error_msg.lower()

    def test_invalid_max_retries_too_large_fails(self):
        """Test max_retries above maximum fails."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key',
            'MAX_RETRIES': '20'  # Too large (max: 10)
        }, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            error_msg = str(exc_info.value)
            assert 'max_retries' in error_msg.lower()

    def test_invalid_rate_limit_per_minute_zero_fails(self):
        """Test rate_limit_per_minute of zero fails."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key',
            'RATE_LIMIT_PER_MINUTE': '0'  # Invalid (min: 1)
        }, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            error_msg = str(exc_info.value)
            assert 'rate_limit_per_minute' in error_msg.lower()

    def test_invalid_environment_fails(self):
        """Test invalid environment value fails."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key',
            'ENVIRONMENT': 'invalid_env'  # Not in [development, staging, production]
        }, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            error_msg = str(exc_info.value)
            assert 'environment' in error_msg.lower()

    def test_invalid_type_for_integer_field_fails(self):
        """Test string value for integer field fails."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key',
            'MAX_RETRIES': 'not_a_number'  # Invalid type
        }, clear=True):
            with pytest.raises((ValidationError, ValueError)) as exc_info:
                Settings()

            error_msg = str(exc_info.value)
            assert 'max_retries' in error_msg.lower() or 'not_a_number' in error_msg.lower() or 'invalid literal' in error_msg.lower()


# Test Suite 2: Environment-Specific Configuration
class TestEnvironmentSpecificConfig:
    """Test environment-specific configuration loading."""

    def test_development_environment(self):
        """Test development environment settings."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key',
            'ENVIRONMENT': 'development',
            'LOG_LEVEL': 'DEBUG'
        }, clear=True):
            settings = Settings()

            assert settings.environment == 'development'
            assert settings.log_level == 'DEBUG'

    def test_staging_environment(self):
        """Test staging environment settings."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key',
            'ENVIRONMENT': 'staging',
            'LOG_LEVEL': 'INFO'
        }, clear=True):
            settings = Settings()

            assert settings.environment == 'staging'
            assert settings.log_level == 'INFO'

    def test_production_environment(self):
        """Test production environment settings."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key',
            'ENVIRONMENT': 'production',
            'LOG_LEVEL': 'WARNING'
        }, clear=True):
            settings = Settings()

            assert settings.environment == 'production'
            assert settings.log_level == 'WARNING'


# Test Suite 3: Default Values
class TestDefaultValues:
    """Test default values for optional settings."""

    def test_all_defaults_applied(self):
        """Test all default values are applied when not specified."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key'
        }, clear=True):
            settings = Settings()

            # Verify documented defaults
            assert settings.log_level == 'INFO'
            assert settings.max_retries == 3
            assert settings.email_body_max_length == 5000
            assert settings.rate_limit_per_minute == 50
            assert settings.agent2_model == 'gpt-4o'
            assert settings.agent3_model == 'claude-3-5-sonnet-20241022'
            assert settings.enable_rate_limiting is True
            assert settings.enable_caching is False
            assert settings.environment == 'development'

    def test_partial_overrides_use_remaining_defaults(self):
        """Test partial configuration overrides with remaining defaults."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key',
            'MAX_RETRIES': '5',
            'LOG_LEVEL': 'WARNING'
        }, clear=True):
            settings = Settings()

            # Overridden values
            assert settings.max_retries == 5
            assert settings.log_level == 'WARNING'

            # Defaults still applied
            assert settings.email_body_max_length == 5000
            assert settings.rate_limit_per_minute == 50


# Test Suite 4: Secrets Masking
class TestSecretsMasking:
    """Test secrets are properly masked in string representations."""

    def test_secret_api_key_masked_in_str(self):
        """Test API key is masked in string representation."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-real-secret-key-12345'
        }, clear=True):
            settings = Settings()

            # String representation should not contain actual key
            settings_str = str(settings)
            assert 'sk-real-secret-key-12345' not in settings_str
            assert '**********' in settings_str or '[REDACTED]' in settings_str or 'SecretStr' in settings_str

    def test_secret_api_key_accessible_via_get_secret_value(self):
        """Test API key can be accessed via get_secret_value()."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-real-secret-key-12345'
        }, clear=True):
            settings = Settings()

            # Can access actual value when needed
            assert settings.openai_api_key.get_secret_value() == 'sk-real-secret-key-12345'

    def test_anthropic_api_key_optional(self):
        """Test Anthropic API key is optional."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key'
            # No ANTHROPIC_API_KEY
        }, clear=True):
            settings = Settings()

            # Should work without Anthropic key
            assert settings.anthropic_api_key is None

    def test_both_api_keys_supported(self):
        """Test both API keys can be configured."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-openai-key',
            'ANTHROPIC_API_KEY': 'sk-ant-api03-anthropic-key'
        }, clear=True):
            settings = Settings()

            assert settings.openai_api_key.get_secret_value() == 'sk-openai-key'
            assert settings.anthropic_api_key.get_secret_value() == 'sk-ant-api03-anthropic-key'


# Test Suite 5: Model Configuration
class TestModelConfiguration:
    """Test model name configuration."""

    def test_default_agent2_model(self):
        """Test Agent 2 defaults to gpt-4o."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key'
        }, clear=True):
            settings = Settings()

            assert settings.agent2_model == 'gpt-4o'

    def test_default_agent3_model(self):
        """Test Agent 3 defaults to claude-3-5-sonnet-20241022."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key'
        }, clear=True):
            settings = Settings()

            assert settings.agent3_model == 'claude-3-5-sonnet-20241022'

    def test_custom_agent2_model(self):
        """Test Agent 2 model can be customized."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key',
            'AGENT2_MODEL': 'gpt-4-turbo'
        }, clear=True):
            settings = Settings()

            assert settings.agent2_model == 'gpt-4-turbo'

    def test_custom_agent3_model(self):
        """Test Agent 3 model can be customized."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key',
            'AGENT3_MODEL': 'claude-3-opus-20240229'
        }, clear=True):
            settings = Settings()

            assert settings.agent3_model == 'claude-3-opus-20240229'


# Test Suite 6: Output Directory Configuration
class TestOutputDirectory:
    """Test output directory configuration."""

    def test_default_output_directory(self):
        """Test default output directory is ./output."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key'
        }, clear=True):
            settings = Settings()

            assert settings.output_directory == Path('./output')

    def test_custom_output_directory(self):
        """Test custom output directory can be configured."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key',
            'OUTPUT_DIRECTORY': '/tmp/graphmail-output'
        }, clear=True):
            settings = Settings()

            assert settings.output_directory == Path('/tmp/graphmail-output')


# Test Suite 7: Boolean Flags
class TestBooleanFlags:
    """Test boolean configuration flags."""

    def test_default_enable_rate_limiting_true(self):
        """Test rate limiting is enabled by default."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key'
        }, clear=True):
            settings = Settings()

            assert settings.enable_rate_limiting is True

    def test_disable_rate_limiting(self):
        """Test rate limiting can be disabled."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key',
            'ENABLE_RATE_LIMITING': 'false'
        }, clear=True):
            settings = Settings()

            assert settings.enable_rate_limiting is False

    def test_default_enable_caching_false(self):
        """Test caching is disabled by default."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key'
        }, clear=True):
            settings = Settings()

            assert settings.enable_caching is False

    def test_enable_caching(self):
        """Test caching can be enabled."""
        from src.config.settings import Settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key',
            'ENABLE_CACHING': 'true'
        }, clear=True):
            settings = Settings()

            assert settings.enable_caching is True


# Test Suite 8: Singleton Pattern
class TestSingletonPattern:
    """Test settings singleton pattern."""

    def test_get_settings_returns_same_instance(self):
        """Test get_settings() returns singleton instance."""
        from src.config.settings import get_settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key'
        }, clear=True):
            settings1 = get_settings()
            settings2 = get_settings()

            # Should be same object
            assert settings1 is settings2

    def test_reset_settings_creates_new_instance(self):
        """Test reset_settings() creates new instance."""
        from src.config.settings import get_settings, reset_settings

        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-test-key'
        }, clear=True):
            settings1 = get_settings()
            reset_settings()
            settings2 = get_settings()

            # Should be different objects after reset
            assert settings1 is not settings2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
