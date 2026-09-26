import logging
from typing import Optional
from .base import BaseLanguageProvider
from .local_qwen import LocalQwenProvider
from .mock_provider import MockLanguageProvider
from ...core.config import settings

logger = logging.getLogger(__name__)

_provider_instance: Optional[BaseLanguageProvider] = None

def get_language_provider() -> BaseLanguageProvider:
    """
    Returns the singleton Language AI provider instance based on runtime settings.
    Defaults to LocalQwenProvider if weights exist and provider_type is 'local',
    or MockLanguageProvider for instant testing/CI.
    """
    global _provider_instance
    if _provider_instance is not None:
        return _provider_instance

    provider_type = settings.LLM_PROVIDER_TYPE.lower()
    
    if provider_type == "local":
        if settings.LLM_MODEL_PATH.exists():
            logger.info("Initializing LocalQwenProvider with GGUF weights...")
            _provider_instance = LocalQwenProvider(model_path=settings.LLM_MODEL_PATH)
        else:
            logger.warning(
                f"Model weights not found at {settings.LLM_MODEL_PATH}. "
                "Falling back to MockLanguageProvider."
            )
            _provider_instance = MockLanguageProvider()
    else:
        logger.info("Initializing MockLanguageProvider (mock/test mode)...")
        _provider_instance = MockLanguageProvider()

    return _provider_instance

__all__ = [
    "BaseLanguageProvider",
    "LocalQwenProvider",
    "MockLanguageProvider",
    "get_language_provider",
]
