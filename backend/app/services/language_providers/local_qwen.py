import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import ValidationError

from .base import BaseLanguageProvider
from ...core.config import settings
from ...schemas.assistant import (
    AssistantLLMOutput,
    AssistantIntentEnum,
    PropertySlots,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are PropValuate AI Assistant, a professional real estate language agent for India.
Analyze user queries, classify intent, extract property attributes, and request tools.

Supported Intents:
- VALUATION_REQUEST: User wants property price estimation. (Requires tool_call: "predict_property_price")
- PROPERTY_INPUT_CLARIFICATION: User omitted required property info (area, BHK, or city). Ask for missing details.
- SUPPORTED_LOCATION_QUERY: User asks about supported cities. (tool_call: "get_supported_locations")
- VALUATION_EXPLANATION: Inquiring about rates, metro distances, or feature breakdown.
- GENERAL_REAL_ESTATE_QUESTION: Conceptual questions (RERA, BHK, carpet area, etc.).
- UNSUPPORTED_REQUEST: Out-of-domain queries (sports, non-property, or cities outside India like London).

STRICT RULE: NEVER calculate or guess numerical property prices. Valuations are strictly performed by the backend tool 'predict_property_price'.

Output Format: You must ALWAYS respond in valid JSON matching this schema:
{
  "intent": "<INTENT_NAME>",
  "reply": "<concise natural language response or question>",
  "tool_call": "<tool_name or null>",
  "slots": {
    "area_sqft": <float or null>,
    "bhk": <int or null>,
    "city": "<string or null>",
    "posted_by": "<Owner|Dealer|Builder or null>",
    "rera": <0|1 or null>,
    "under_construction": <0|1 or null>,
    "ready_to_move": <0|1 or null>,
    "resale": <0|1 or null>,
    "is_rk": <0|1 or null>
  },
  "missing_slots": ["<slot_name>", ...]
}
"""

def extract_json_from_text(raw_text: str) -> Optional[Dict[str, Any]]:
    """Extracts and parses JSON object from model output text."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace >= first_brace:
        json_str = text[first_brace:last_brace + 1]
        try:
            return json.loads(json_str)
        except Exception:
            pass
    try:
        return json.loads(text)
    except Exception:
        return None

class LocalQwenProvider(BaseLanguageProvider):
    """
    Local Small Language Model Provider using Qwen2.5-3B-Instruct (GGUF Q4_K_M)
    via llama-cpp-python with CPU AVX2 acceleration.
    """

    def __init__(self, model_path: Optional[Path] = None):
        self._model_path = model_path or settings.LLM_MODEL_PATH
        self._llm = None
        self._is_loaded = False

    def load(self) -> None:
        """Loads the GGUF model once into memory."""
        if self._is_loaded and self._llm is not None:
            return

        if not self._model_path.exists():
            logger.warning(
                f"Local LLM model file not found at {self._model_path}. "
                "LocalQwenProvider will remain uninitialized."
            )
            return

        try:
            import llama_cpp
            logger.info(f"Loading local Qwen GGUF model from {self._model_path}...")
            self._llm = llama_cpp.Llama(
                model_path=str(self._model_path),
                n_ctx=settings.LLM_CONTEXT_WINDOW,
                n_threads=settings.LLM_THREADS,
                verbose=False,
            )
            self._is_loaded = True
            logger.info("Local Qwen GGUF model successfully loaded.")
        except Exception as e:
            logger.error(f"Failed to load local Qwen model: {str(e)}")
            self._is_loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded and self._llm is not None

    @property
    def model_name(self) -> str:
        return "Qwen2.5-3B-Instruct (GGUF Q4_K_M)"

    def extract_structured_intent(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 180,
        temperature: float = 0.1,
    ) -> AssistantLLMOutput:
        """
        Executes ChatML completion with Qwen 2.5 and extracts validated AssistantLLMOutput.
        """
        if not self.is_loaded:
            logger.warning("LocalQwenProvider is not loaded. Using fallback rule parser.")
            return self._heuristic_fallback(messages[-1]["content"] if messages else "")

        # Format conversation with system prompt
        formatted_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        # Add past dialogue turns (up to last 6 turns to keep context fast)
        for msg in messages[-6:]:
            formatted_messages.append({"role": msg["role"], "content": msg["content"]})

        try:
            response = self._llm.create_chat_completion(
                messages=formatted_messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            raw_content = response["choices"][0]["message"]["content"]
            parsed_json = extract_json_from_text(raw_content)

            if parsed_json and isinstance(parsed_json, dict):
                try:
                    return AssistantLLMOutput(**parsed_json)
                except ValidationError as ve:
                    logger.warning(f"Schema validation warning on model output: {ve}. Sanitizing output.")
                    # Build sanitized output
                    return self._sanitize_parsed_dict(parsed_json)

            logger.warning(f"Could not parse model output as JSON: {raw_content[:150]}. Using heuristic recovery.")
            return self._heuristic_fallback(messages[-1]["content"] if messages else "")

        except Exception as e:
            logger.exception(f"Error during LLM chat completion: {e}")
            return self._heuristic_fallback(messages[-1]["content"] if messages else "")

    def generate_concise_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 150,
        temperature: float = 0.2,
    ) -> str:
        """Generates concise text response."""
        if not self.is_loaded:
            return "PropValuate AI is a specialized real estate valuation platform for India."

        formatted_messages = [
            {
                "role": "system",
                "content": "You are PropValuate AI. Provide a concise, helpful 1-2 sentence real estate answer.",
            }
        ]
        for msg in messages[-4:]:
            formatted_messages.append({"role": msg["role"], "content": msg["content"]})

        try:
            response = self._llm.create_chat_completion(
                messages=formatted_messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"Error generating concise response: {e}")
            return "I am here to assist you with property valuations across India."

    def _sanitize_parsed_dict(self, d: Dict[str, Any]) -> AssistantLLMOutput:
        """Sanitizes imperfect model dictionary into valid AssistantLLMOutput."""
        intent_raw = str(d.get("intent", "GENERAL_REAL_ESTATE_QUESTION")).upper()
        try:
            intent = AssistantIntentEnum(intent_raw)
        except ValueError:
            intent = AssistantIntentEnum.GENERAL_REAL_ESTATE_QUESTION

        reply = str(d.get("reply", "How can I assist you with your property valuation today?"))
        tool_call = d.get("tool_call")
        if tool_call not in {"predict_property_price", "get_supported_locations"}:
            tool_call = None

        raw_slots = d.get("slots", {})
        if not isinstance(raw_slots, dict):
            raw_slots = {}

        # Safely extract and bound-check slot values
        area_val = None
        if raw_slots.get("area_sqft") is not None:
            try:
                parsed_area = float(raw_slots["area_sqft"])
                if 0 < parsed_area <= 50000:
                    area_val = parsed_area
            except (ValueError, TypeError):
                pass

        bhk_val = None
        if raw_slots.get("bhk") is not None:
            try:
                parsed_bhk = int(raw_slots["bhk"])
                if 1 <= parsed_bhk <= 20:
                    bhk_val = parsed_bhk
            except (ValueError, TypeError):
                pass

        def get_binary_flag(key: str) -> Optional[int]:
            if raw_slots.get(key) is not None:
                try:
                    flag = int(raw_slots[key])
                    return flag if flag in {0, 1} else None
                except (ValueError, TypeError):
                    return None
            return None

        slots = PropertySlots(
            area_sqft=area_val,
            bhk=bhk_val,
            city=str(raw_slots["city"]) if raw_slots.get("city") is not None else None,
            posted_by=str(raw_slots["posted_by"]) if raw_slots.get("posted_by") is not None else None,
            rera=get_binary_flag("rera"),
            under_construction=get_binary_flag("under_construction"),
            ready_to_move=get_binary_flag("ready_to_move"),
            resale=get_binary_flag("resale"),
            is_rk=get_binary_flag("is_rk"),
        )

        missing_slots = d.get("missing_slots", [])
        if not isinstance(missing_slots, list):
            missing_slots = []

        return AssistantLLMOutput(
            intent=intent,
            reply=reply,
            tool_call=tool_call,
            slots=slots,
            missing_slots=[str(s) for s in missing_slots],
        )

    def _heuristic_fallback(self, user_text: str) -> AssistantLLMOutput:
        """Deterministic rule-based fallback when model is unavailable or malformed."""
        from .mock_provider import MockLanguageProvider
        mock = MockLanguageProvider()
        return mock.extract_structured_intent([{"role": "user", "content": user_text}])
