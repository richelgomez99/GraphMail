"""
Centralized Configuration Management

Type-safe configuration using Pydantic BaseSettings.
Externalizes all hardcoded values (paths, limits, timeouts, models).

Features:
- Environment variable loading with .env support
- Type validation with clear error messages
- Sensible defaults for optional settings
- Secrets masking (SecretStr)
- Singleton pattern for global access

Configuration Priority (highest to lowest):
1. Environment variables (set in shell)
2. .env file
3. Default values

Constitutional Alignment:
- Article VII: API-First Design (enables environment-specific deployments)
- Article VI: Test-Driven Development (type-safe prevents runtime errors)
- Article VIII: Security by Default (secrets masked, never logged)
"""

from typing import Optional, Literal
from pathlib import Path
from pydantic import BaseModel, Field, field_validator, SecretStr
import os
from dotenv import load_dotenv
import structlog

logger = structlog.get_logger(__name__)


# Load .env file if it exists
load_dotenv()


# Environment type
Environment = Literal['development', 'staging', 'production']

# Log level type
LogLevel = Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']


def _get_env_or_default(key: str, default: str) -> str:
    """Get environment variable or return default."""
    return os.getenv(key, default)


class Settings(BaseModel):
    """
    Centralized configuration for GRAPHMAIL.

    All configuration values are loaded from environment variables or .env file.
    Type validation ensures invalid configuration is caught at startup.

    Example .env file:
        ENVIRONMENT=development
        LOG_LEVEL=DEBUG
        OPENAI_API_KEY=sk-...
        EMAIL_BODY_MAX_LENGTH=5000
        MAX_RETRIES=3
        RATE_LIMIT_PER_MINUTE=50

    Constitutional Alignment:
        - Article VII: API-First Design
        - Article VI: Test-Driven Development
        - Article VIII: Security by Default
    """

    # ========================================
    # Environment Configuration
    # ========================================

    environment: Environment = Field(
        default='development',
        description="Deployment environment: development, staging, or production"
    )

    # ========================================
    # Logging Configuration
    # ========================================

    log_level: LogLevel = Field(
        default='INFO',
        description="Log verbosity level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )

    # ========================================
    # API Keys (Secrets)
    # ========================================

    openai_api_key: Optional[SecretStr] = Field(
        default=None,
        description="OpenAI API key for GPT models (masked in logs)"
    )

    anthropic_api_key: Optional[SecretStr] = Field(
        default=None,
        description="Anthropic API key for Claude models (masked in logs)"
    )

    # ========================================
    # Email Processing Configuration
    # ========================================

    email_body_max_length: int = Field(
        default=5000,
        ge=1000,
        le=10000,
        description="Maximum email body length in characters (1000-10000)"
    )

    # ========================================
    # Retry Configuration
    # ========================================

    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts for LLM API calls (0-10)"
    )

    retry_base_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Base delay for exponential backoff in seconds (0.1-10.0)"
    )

    retry_max_total_time: float = Field(
        default=10.0,
        ge=1.0,
        le=60.0,
        description="Maximum total retry time in seconds (1.0-60.0)"
    )

    # ========================================
    # Rate Limiting Configuration
    # ========================================

    rate_limit_per_minute: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Maximum LLM API calls per minute (1-1000)"
    )

    enable_rate_limiting: bool = Field(
        default=True,
        description="Enable rate limiting for LLM API calls"
    )

    # ========================================
    # Model Configuration
    # ========================================

    agent2_model: str = Field(
        default='gpt-4o',
        description="Model name for Agent 2 (Extractor)"
    )

    agent3_model: str = Field(
        default='claude-3-5-sonnet-20241022',
        description="Model name for Agent 3 (Verifier)"
    )

    # ========================================
    # File System Configuration
    # ========================================

    output_directory: Path = Field(
        default=Path('./output'),
        description="Directory for output files (graphs, reports)"
    )

    # ========================================
    # Feature Flags
    # ========================================

    enable_caching: bool = Field(
        default=False,
        description="Enable LLM response caching (future feature)"
    )

    # ========================================
    # Constructor
    # ========================================

    def __init__(self, **kwargs):
        """
        Initialize Settings from environment variables.

        Loads configuration from environment variables with proper type conversion.
        Falls back to provided kwargs or defaults if env vars not set.
        """
        # Load from environment variables, with kwargs taking precedence
        env_config = {
            'environment': os.getenv('ENVIRONMENT', kwargs.get('environment', 'development')),
            'log_level': os.getenv('LOG_LEVEL', kwargs.get('log_level', 'INFO')),
            'openai_api_key': SecretStr(os.getenv('OPENAI_API_KEY')) if os.getenv('OPENAI_API_KEY') else kwargs.get('openai_api_key'),
            'anthropic_api_key': SecretStr(os.getenv('ANTHROPIC_API_KEY')) if os.getenv('ANTHROPIC_API_KEY') else kwargs.get('anthropic_api_key'),
            'email_body_max_length': int(os.getenv('EMAIL_BODY_MAX_LENGTH', str(kwargs.get('email_body_max_length', 5000)))),
            'max_retries': int(os.getenv('MAX_RETRIES', str(kwargs.get('max_retries', 3)))),
            'retry_base_delay': float(os.getenv('RETRY_BASE_DELAY', str(kwargs.get('retry_base_delay', 1.0)))),
            'retry_max_total_time': float(os.getenv('RETRY_MAX_TOTAL_TIME', str(kwargs.get('retry_max_total_time', 10.0)))),
            'rate_limit_per_minute': int(os.getenv('RATE_LIMIT_PER_MINUTE', str(kwargs.get('rate_limit_per_minute', 50)))),
            'enable_rate_limiting': os.getenv('ENABLE_RATE_LIMITING', str(kwargs.get('enable_rate_limiting', 'true'))).lower() == 'true',
            'agent2_model': os.getenv('AGENT2_MODEL', kwargs.get('agent2_model', 'gpt-4o')),
            'agent3_model': os.getenv('AGENT3_MODEL', kwargs.get('agent3_model', 'claude-3-5-sonnet-20241022')),
            'output_directory': Path(os.getenv('OUTPUT_DIRECTORY', kwargs.get('output_directory', './output'))),
            'enable_caching': os.getenv('ENABLE_CACHING', str(kwargs.get('enable_caching', 'false'))).lower() == 'true',
        }

        # Call parent __init__ with env_config
        super().__init__(**env_config)

        # Validate that at least one API key is provided
        if not self.openai_api_key and not self.anthropic_api_key:
            raise ValueError(
                "At least one API key must be provided: OPENAI_API_KEY or ANTHROPIC_API_KEY"
            )

        # Log configuration loaded (with secrets masked)
        logger.info(
            "config.loaded",
            environment=self.environment,
            log_level=self.log_level,
            has_openai_key=self.openai_api_key is not None,
            has_anthropic_key=self.anthropic_api_key is not None,
            email_body_max_length=self.email_body_max_length,
            max_retries=self.max_retries,
            rate_limit_per_minute=self.rate_limit_per_minute,
            agent2_model=self.agent2_model,
            agent3_model=self.agent3_model
        )


# ========================================
# Singleton Pattern
# ========================================

_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get singleton Settings instance.

    Returns:
        Settings: Global settings instance

    Example:
        >>> from src.config import get_settings
        >>> settings = get_settings()
        >>> print(settings.max_retries)
        3
    """
    global _settings

    if _settings is None:
        _settings = Settings()

    return _settings


def reset_settings() -> None:
    """
    Reset singleton Settings instance.

    Useful for testing to force reloading configuration.

    Example:
        >>> from src.config import reset_settings
        >>> reset_settings()  # Force reload on next get_settings()
    """
    global _settings
    _settings = None
    logger.debug("config.reset")
