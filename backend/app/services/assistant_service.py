import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from ..schemas.assistant import (
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantIntentEnum,
    AssistantLLMOutput,
    PropertySlots,
)
from .session_manager import session_manager, AssistantSession
from .capability_router import capability_router
from .language_providers import get_language_provider
from .geo_service import resolve_city_coordinates
from ..core.config import settings

logger = logging.getLogger(__name__)

class AssistantService:
    """
    Main Orchestrator for PropValuate AI Language Assistant.
    Coordinates session state, LLM structured extraction, Pydantic schema validation,
    deterministic tool execution, and grounded response composition.
    """

    def __init__(self):
        self._provider = None

    @property
    def provider(self):
        if self._provider is None:
            self._provider = get_language_provider()
        return self._provider

    def process_message(self, request: AssistantChatRequest) -> AssistantChatResponse:
        """
        Executes complete conversational assistant cycle:
        1. Validates input bounds.
        2. Retrieves bounded session.
        3. Extracts structured intent & slots via LLM provider.
        4. Accumulates slot state.
        5. Executes authorized tools deterministically.
        6. Composes grounded user response.
        """
        user_message = request.message.strip()
        session: AssistantSession = session_manager.get_or_create_session(request.session_id)
        session.add_message(role="user", content=user_message)

        # 1. Extract structured intent and slots from LLM
        llm_output: AssistantLLMOutput = self.provider.extract_structured_intent(
            messages=session.messages,
            max_tokens=settings.LLM_MAX_TOKENS,
            temperature=settings.LLM_TEMPERATURE,
        )

        # 2. Merge extracted slots into session accumulator
        if llm_output.slots:
            session.merge_slots(llm_output.slots)

        accumulated = session.accumulated_slots
        current_intent = llm_output.intent
        tool_called: Optional[str] = None
        tool_result: Optional[Dict[str, Any]] = None
        final_reply = llm_output.reply
        is_valuation_complete = False
        missing_slots: List[str] = []

        # 3. Process Intent & Routing Logic
        if current_intent == AssistantIntentEnum.UNSUPPORTED_REQUEST:
            final_reply = (
                "PropValuate AI is specialized for residential property valuations in India. "
                "For property inquiries, please specify an Indian city (e.g. Bangalore, Mumbai, Pune), "
                "area in sqft, and BHK."
            )

        elif current_intent == AssistantIntentEnum.SUPPORTED_LOCATION_QUERY:
            tool_called = "get_supported_locations"
            loc_res = capability_router.execute_tool("get_supported_locations")
            if loc_res.status == "success" and loc_res.data:
                tool_result = loc_res.data
                cities_sample = ", ".join(loc_res.data["locations"][:12])
                final_reply = (
                    f"PropValuate AI currently supports {loc_res.data['total_count']} major Indian cities and municipalities, "
                    f"including {cities_sample}, and many more."
                )

        elif current_intent in {
            AssistantIntentEnum.VALUATION_REQUEST,
            AssistantIntentEnum.PROPERTY_INPUT_CLARIFICATION,
        }:
            # Check city validity if present
            if accumulated.city:
                coords = resolve_city_coordinates(accumulated.city)
                if not coords:
                    current_intent = AssistantIntentEnum.UNSUPPORTED_REQUEST
                    final_reply = (
                        f"Location '{accumulated.city.title()}' is not currently in the verified 81-city registry. "
                        "Please select a supported Indian city such as Bangalore, Mumbai, Delhi-NCR, Pune, Hyderabad, or Chennai."
                    )
                    return self._build_response(
                        session_id=session.session_id,
                        reply=final_reply,
                        intent=current_intent,
                        tool_called=None,
                        tool_result=None,
                        slots=accumulated,
                        missing_slots=["city"],
                        is_valuation_complete=False,
                    )

            # Check mandatory slot completeness
            if accumulated.area_sqft is None or accumulated.area_sqft <= 0:
                missing_slots.append("area_sqft")
            if accumulated.bhk is None or accumulated.bhk < 1:
                missing_slots.append("bhk")
            if not accumulated.city:
                missing_slots.append("city")

            if missing_slots:
                current_intent = AssistantIntentEnum.PROPERTY_INPUT_CLARIFICATION
                missing_labels = [s.replace("_", " ").title() for s in missing_slots]
                final_reply = (
                    f"To calculate an accurate valuation, please provide the property's: {', '.join(missing_labels)}."
                )
            else:
                # All mandatory fields present -> Execute authoritative valuation tool
                current_intent = AssistantIntentEnum.VALUATION_REQUEST
                tool_called = "predict_property_price"
                val_res = capability_router.execute_tool(
                    tool_name="predict_property_price",
                    slots=accumulated
                )
                
                if val_res.status == "success" and val_res.data:
                    tool_result = val_res.data
                    is_valuation_complete = True
                    price_lakhs = val_res.data["predicted_price_lakhs"]
                    rate_sqft = val_res.data["rate_per_sqft"]
                    city_name = accumulated.city.title()
                    
                    final_reply = (
                        f"The estimated market valuation for a {accumulated.bhk} BHK ({accumulated.area_sqft} sqft) "
                        f"apartment in {city_name} is ₹{price_lakhs:,.2f} Lakhs (approx. ₹{rate_sqft:,.2f}/sqft). "
                        "This prediction is computed deterministically by Valuation Engine V2."
                    )
                else:
                    final_reply = f"Valuation could not be completed: {val_res.error or 'Internal calculation error.'}"

        # 4. Record assistant reply into session history
        session.add_message(role="assistant", content=final_reply)

        return self._build_response(
            session_id=session.session_id,
            reply=final_reply,
            intent=current_intent,
            tool_called=tool_called,
            tool_result=tool_result,
            slots=accumulated,
            missing_slots=missing_slots,
            is_valuation_complete=is_valuation_complete,
        )

    def _build_response(
        self,
        session_id: str,
        reply: str,
        intent: AssistantIntentEnum,
        tool_called: Optional[str],
        tool_result: Optional[Dict[str, Any]],
        slots: PropertySlots,
        missing_slots: List[str],
        is_valuation_complete: bool,
    ) -> AssistantChatResponse:
        return AssistantChatResponse(
            session_id=session_id,
            reply=reply,
            intent=intent,
            tool_called=tool_called,
            tool_result=tool_result,
            slots=slots,
            missing_slots=missing_slots,
            is_valuation_complete=is_valuation_complete,
            model_name=self.provider.model_name,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

assistant_service = AssistantService()
