import pytest
from pydantic import ValidationError
from backend.app.schemas.assistant import (
    AssistantIntentEnum,
    PropertySlots,
    AssistantLLMOutput,
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantResetResponse,
)

def test_property_slots_validation_valid():
    slots = PropertySlots(
        area_sqft=1500.0,
        bhk=3,
        city="Bangalore",
        posted_by="owner",
        rera=1,
        under_construction=0,
        ready_to_move=1,
        resale=1,
        is_rk=0
    )
    assert slots.area_sqft == 1500.0
    assert slots.bhk == 3
    assert slots.city == "bangalore"  # Normalized to lowercase
    assert slots.posted_by == "Owner"  # Normalized to title case
    assert slots.rera == 1
    assert slots.ready_to_move == 1

def test_property_slots_invalid_ranges():
    # Negative area
    with pytest.raises(ValidationError):
        PropertySlots(area_sqft=-50.0)

    # Excessive area
    with pytest.raises(ValidationError):
        PropertySlots(area_sqft=100000.0)

    # Negative BHK
    with pytest.raises(ValidationError):
        PropertySlots(bhk=0)

    # Invalid RERA flag
    with pytest.raises(ValidationError):
        PropertySlots(rera=2)

def test_assistant_chat_request_validation():
    # Valid request
    req = AssistantChatRequest(message="Hello, estimate my property price.")
    assert req.message == "Hello, estimate my property price."
    assert req.session_id is None

    # Empty message rejection
    with pytest.raises(ValidationError):
        AssistantChatRequest(message="   ")

    # Length limit rejection (> 1000 chars)
    with pytest.raises(ValidationError):
        AssistantChatRequest(message="a" * 1001)

def test_assistant_llm_output_serialization():
    out = AssistantLLMOutput(
        intent=AssistantIntentEnum.VALUATION_REQUEST,
        reply="Estimating valuation for 3 BHK in Bangalore...",
        tool_call="predict_property_price",
        slots=PropertySlots(area_sqft=1500.0, bhk=3, city="bangalore"),
        missing_slots=[]
    )
    dumped = out.model_dump()
    assert dumped["intent"] == "VALUATION_REQUEST"
    assert dumped["tool_call"] == "predict_property_price"
    assert dumped["slots"]["area_sqft"] == 1500.0
    assert dumped["slots"]["city"] == "bangalore"
