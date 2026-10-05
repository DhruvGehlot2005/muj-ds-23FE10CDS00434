"""
@file config.py
@description Central configuration management using Pydantic Settings and YAML configuration
@module backend.app.config
"""

import os
from typing import Any, Dict, Optional, Tuple
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


def _load_yaml_config() -> Dict[str, Any]:
    """Loads configuration dictionary from YAML files if PyYAML is available."""
    try:
        import yaml
    except ImportError:
        return {}

    candidate_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.yaml"),
        os.path.join(os.path.dirname(__file__), "config.yaml"),
        "config.yaml",
    ]

    for path in candidate_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict):
                        return data
            except Exception:
                pass
    return {}


def _get_yaml_defaults() -> Dict[str, Any]:
    """Flattens nested YAML configuration into settings keys."""
    data = _load_yaml_config()
    server = data.get("server", {}) if isinstance(data.get("server"), dict) else {}
    llm = data.get("llm", {}) if isinstance(data.get("llm"), dict) else {}
    sec = data.get("security", {}) if isinstance(data.get("security"), dict) else {}

    defaults: Dict[str, Any] = {}
    if "host" in server:
        defaults["backend_host"] = server["host"]
    if "port" in server:
        defaults["backend_port"] = server["port"]
    if "frontend_url" in server:
        defaults["frontend_url"] = server["frontend_url"]

    if "provider" in llm:
        defaults["llm_provider"] = llm["provider"]
    if "model" in llm:
        defaults["llm_model"] = llm["model"]
    if llm.get("api_key"):
        defaults["llm_api_key"] = llm["api_key"]

    if "max_upload_size_mb" in sec:
        defaults["max_upload_size_mb"] = sec["max_upload_size_mb"]
    if "rate_limit_per_minute" in sec:
        defaults["rate_limit_per_minute"] = sec["rate_limit_per_minute"]
    if "section_classifier_confidence_threshold" in sec:
        defaults["section_classifier_confidence_threshold"] = sec["section_classifier_confidence_threshold"]
    if "log_level" in sec:
        defaults["log_level"] = sec["log_level"]

    return defaults


class _YamlSettingsSource(PydanticBaseSettingsSource):
    """Pydantic Settings source that reads defaults from config.yaml."""

    def get_field_value(self, field: Any, field_name: str) -> Tuple[Any, str, bool]:
        return None, field_name, False

    def __call__(self) -> Dict[str, Any]:
        return _get_yaml_defaults()


class Settings(BaseSettings):
    """Application settings loaded from YAML, environment variables, and .env file."""

    model_config = SettingsConfigDict(
        env_file=(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
            ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM Settings
    llm_api_key: str = "mock-key-for-local-testing"
    llm_model: str = "gemini-3.5-flash-lite"
    llm_provider: str = "gemini"

    # Server Settings
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:3000"

    # Limits & Security
    max_upload_size_mb: int = 10
    rate_limit_per_minute: int = 30
    section_classifier_confidence_threshold: float = 0.60
    log_level: str = "INFO"

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            _YamlSettingsSource(settings_cls),
            file_secret_settings,
        )

    @property
    def max_upload_size_bytes(self) -> int:
        """Returns the maximum upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024


settings = Settings()
