from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ...schemas.assistant import AssistantLLMOutput

class BaseLanguageProvider(ABC):
    """
    Abstract base provider class for Language AI models.
    Enables pluggable switching between Local Qwen GGUF and future hosted/cloud providers
    without modifying the assistant orchestration or capability router.
    """

    @abstractmethod
    def load(self) -> None:
        """Loads model weights or initializes the provider client."""
        pass

    @property
    @abstractmethod
    def is_loaded(self) -> bool:
        """Returns True if the provider is initialized and ready for inference."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Returns the canonical model name or identifier."""
        pass

    @abstractmethod
    def extract_structured_intent(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 180,
        temperature: float = 0.1
    ) -> AssistantLLMOutput:
        """
        Parses dialogue history and extracts classified intent, property slots,
        requested tool call, and natural-language reply in strict AssistantLLMOutput format.
        """
        pass

    @abstractmethod
    def generate_concise_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 150,
        temperature: float = 0.2
    ) -> str:
        """
        Generates a concise conversational explanation or response for general questions.
        """
        pass
