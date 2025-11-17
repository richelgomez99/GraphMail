"""
Configuration Management Module

Centralized, type-safe configuration system for GRAPHMAIL.

Exports:
    - Settings: Pydantic BaseSettings model with all configuration
    - get_settings: Singleton function to get settings instance
    - reset_settings: Reset singleton (useful for testing)

Constitutional Alignment:
- Article VII: API-First Design
- Article VI: Test-Driven Development
- Article VIII: Security by Default
"""

from .settings import Settings, get_settings, reset_settings

__all__ = ['Settings', 'get_settings', 'reset_settings']
