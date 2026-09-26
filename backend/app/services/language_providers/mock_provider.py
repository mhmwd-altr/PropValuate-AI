import re
from typing import List, Dict, Any, Optional
from .base import BaseLanguageProvider
from ...schemas.assistant import (
    AssistantLLMOutput,
    AssistantIntentEnum,
    PropertySlots,
)
from ..geo_service import CITY_CENTROIDS, COORD_ALIASES

class MockLanguageProvider(BaseLanguageProvider):
    """
    Deterministic Rule-Based / Mock Language AI Provider.
    Enables instant (<1ms) testing, CI pipelines, and resilient fallback execution.
    """

    def __init__(self):
        self._is_loaded = True

    def load(self) -> None:
        self._is_loaded = True

    @property
    def is_loaded(self) -> bool:
        return True

    @property
    def model_name(self) -> str:
        return "Deterministic Rule/Mock Provider"

    def extract_structured_intent(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 180,
        temperature: float = 0.1,
    ) -> AssistantLLMOutput:
        user_text = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_text = msg.get("content", "")
                break

        text_lower = user_text.lower()

        # 1. Check out of domain / unsupported queries
        out_of_domain_keywords = ["weather", "cricket", "recipe", "python code", "football", "president", "stocks"]
        if any(kw in text_lower for kw in out_of_domain_keywords):
            return AssistantLLMOutput(
                intent=AssistantIntentEnum.UNSUPPORTED_REQUEST,
                reply="I am specialized in Indian real estate property valuations. Please ask a property-related question.",
                tool_call=None,
                slots=PropertySlots(),
                missing_slots=[],
            )

        # Check unsupported foreign cities
        foreign_cities = ["london", "new york", "dubai", "paris", "tokyo", "singapore", "toronto"]
        if any(fc in text_lower for fc in foreign_cities):
            return AssistantLLMOutput(
                intent=AssistantIntentEnum.UNSUPPORTED_REQUEST,
                reply="I only support property valuations for cities in India. Locations outside India are currently unsupported.",
                tool_call=None,
                slots=PropertySlots(),
                missing_slots=[],
            )

        # 2. Check Supported Locations Query
        if any(kw in text_lower for kw in ["which cities", "supported cities", "covered cities", "what cities", "cities do you support", "list of cities", "is pune covered"]):
            return AssistantLLMOutput(
                intent=AssistantIntentEnum.SUPPORTED_LOCATION_QUERY,
                reply="PropValuate AI supports 81 major Indian cities including Bangalore, Mumbai, Delhi-NCR, Pune, Hyderabad, Chennai, and Kolkata.",
                tool_call="get_supported_locations",
                slots=PropertySlots(),
                missing_slots=[],
            )

        # 3. Check General Real Estate Concept / Explanation Questions
        concept_keywords = ["what is rera", "explain rera", "what is bhk", "what is carpet area", "difference between carpet", "super built-up", "what is rk"]
        if any(kw in text_lower for kw in concept_keywords):
            reply_map = {
                "rera": "RERA (Real Estate Regulatory Authority) provides transparency, protects home buyers, and mandates standardized carpet area disclosures for Indian real estate projects.",
                "bhk": "BHK stands for Bedroom, Hall, and Kitchen, standard terminology denoting residential flat unit configurations in India.",
                "rk": "RK stands for Room-Kitchen studio layout, typically a single living/sleeping room with a separate kitchenette and bath.",
            }
            matched_reply = "In Indian real estate, standard regulatory and structural designations guide property specifications and valuation."
            for k, ans in reply_map.items():
                if k in text_lower:
                    matched_reply = ans
                    break
            return AssistantLLMOutput(
                intent=AssistantIntentEnum.GENERAL_REAL_ESTATE_QUESTION,
                reply=matched_reply,
                tool_call=None,
                slots=PropertySlots(),
                missing_slots=[],
            )

        # 4. Extract Slots for Valuation Intent
        slots = PropertySlots()
        
        # Area extraction (e.g. "1500 sqft", "1200 square feet", "1500 sq ft", "1500sqft")
        area_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:sqft|sq\.?\s*ft|square\s*feet|sq\s*feet|sq\s*meters)', text_lower)
        if area_match:
            try:
                slots.area_sqft = float(area_match.group(1))
            except ValueError:
                pass

        # BHK extraction (e.g. "3 bhk", "3bhk", "2 bedroom", "3-bhk", "1 rk")
        bhk_match = re.search(r'(\d+)\s*(?:bhk|bedroom|bed|\-bhk)', text_lower)
        if bhk_match:
            try:
                slots.bhk = int(bhk_match.group(1))
            except ValueError:
                pass
        elif "1 rk" in text_lower or "1rk" in text_lower:
            slots.bhk = 1
            slots.is_rk = 1

        # City extraction
        for city_key in CITY_CENTROIDS.keys():
            # Check with word boundary
            pattern = r'\b' + re.escape(city_key.replace("-", " ")) + r'\b'
            if re.search(pattern, text_lower) or city_key in text_lower:
                slots.city = city_key
                break
        if not slots.city:
            for alias, canonical in COORD_ALIASES.items():
                pattern = r'\b' + re.escape(alias) + r'\b'
                if re.search(pattern, text_lower):
                    slots.city = canonical
                    break

        # Additional attributes
        if "rera" in text_lower or "rera approved" in text_lower or "rera registered" in text_lower:
            slots.rera = 1
        elif "non-rera" in text_lower or "without rera" in text_lower:
            slots.rera = 0

        if "resale" in text_lower:
            slots.resale = 1
        elif "new construction" in text_lower or "direct from builder" in text_lower or "builder sale" in text_lower:
            slots.resale = 0

        if "ready to move" in text_lower or "ready-to-move" in text_lower:
            slots.ready_to_move = 1
            slots.under_construction = 0
        elif "under construction" in text_lower or "under-construction" in text_lower:
            slots.under_construction = 1
            slots.ready_to_move = 0

        if "owner" in text_lower:
            slots.posted_by = "Owner"
        elif "dealer" in text_lower or "agent" in text_lower or "broker" in text_lower:
            slots.posted_by = "Dealer"
        elif "builder" in text_lower or "developer" in text_lower:
            slots.posted_by = "Builder"

        # Determine if this is a valuation request or clarification
        is_val_query = any(kw in text_lower for kw in [
            "estimate", "price", "valuation", "value", "calculate", "worth", "how much", "cost", "flat", "apartment"
        ])

        if is_val_query or slots.area_sqft or slots.bhk or slots.city:
            missing = []
            if not slots.area_sqft:
                missing.append("area_sqft")
            if not slots.bhk:
                missing.append("bhk")
            if not slots.city:
                missing.append("city")

            if not missing:
                return AssistantLLMOutput(
                    intent=AssistantIntentEnum.VALUATION_REQUEST,
                    reply=f"Estimating valuation for a {slots.bhk} BHK property of {slots.area_sqft} sqft in {slots.city.title()}...",
                    tool_call="predict_property_price",
                    slots=slots,
                    missing_slots=[],
                )
            else:
                missing_str = ", ".join([s.replace("_", " ") for s in missing])
                return AssistantLLMOutput(
                    intent=AssistantIntentEnum.PROPERTY_INPUT_CLARIFICATION,
                    reply=f"To calculate an accurate valuation, please provide the property's: {missing_str}.",
                    tool_call=None,
                    slots=slots,
                    missing_slots=missing,
                )

        # Default general reply
        return AssistantLLMOutput(
            intent=AssistantIntentEnum.GENERAL_REAL_ESTATE_QUESTION,
            reply="Hello! I am PropValuate AI Assistant. I can help you estimate property prices across 81 Indian cities or answer real estate questions.",
            tool_call=None,
            slots=PropertySlots(),
            missing_slots=[],
        )

    def generate_concise_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 150,
        temperature: float = 0.2,
    ) -> str:
        return "PropValuate AI delivers deterministic machine-learning residential property valuations across India."
