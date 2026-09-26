import pytest
from backend.app.services.assistant_service import assistant_service
from backend.app.schemas.assistant import AssistantChatRequest, AssistantIntentEnum
from backend.app.services.model_service_v2 import model_service_v2
from backend.app.services.location_service import location_service
from backend.app.services.language_providers.mock_provider import MockLanguageProvider

@pytest.fixture(autouse=True)
def setup_environment():
    if not model_service_v2.is_loaded:
        model_service_v2.load()
    if not location_service.is_loaded:
        location_service.load()
    # Use deterministic mock provider for unit tests to ensure <10ms execution
    assistant_service._provider = MockLanguageProvider()

def test_assistant_full_valuation_intent():
    req = AssistantChatRequest(
        message="I want to estimate the price of a 1500 sqft 3 BHK apartment in Bangalore."
    )
    res = assistant_service.process_message(req)
    assert res.intent == AssistantIntentEnum.VALUATION_REQUEST
    assert res.is_valuation_complete is True
    assert res.tool_called == "predict_property_price"
    assert res.tool_result is not None
    assert res.tool_result["predicted_price_lakhs"] > 0
    assert "₹" in res.reply
    assert "Lakhs" in res.reply

def test_assistant_multi_turn_slot_filling():
    # Turn 1: User gives area only
    req1 = AssistantChatRequest(message="I have an apartment with 1500 sqft area.")
    res1 = assistant_service.process_message(req1)
    assert res1.intent == AssistantIntentEnum.PROPERTY_INPUT_CLARIFICATION
    assert res1.is_valuation_complete is False
    assert "bhk" in res1.missing_slots
    assert "city" in res1.missing_slots
    session_id = res1.session_id

    # Turn 2: User provides BHK and city in same session
    req2 = AssistantChatRequest(session_id=session_id, message="It is a 3 BHK in Mumbai.")
    res2 = assistant_service.process_message(req2)
    assert res2.intent == AssistantIntentEnum.VALUATION_REQUEST
    assert res2.is_valuation_complete is True
    assert res2.slots.area_sqft == 1500.0
    assert res2.slots.bhk == 3
    assert res2.slots.city == "mumbai"

def test_assistant_unsupported_location():
    req = AssistantChatRequest(
        message="Estimate the price of my 1500 sqft 3 BHK apartment in London."
    )
    res = assistant_service.process_message(req)
    assert res.intent == AssistantIntentEnum.UNSUPPORTED_REQUEST
    assert res.is_valuation_complete is False
    assert res.tool_called is None
    assert "supported" in res.reply.lower() or "india" in res.reply.lower()

def test_assistant_supported_cities_query():
    req = AssistantChatRequest(
        message="Which cities do you support for property valuation?"
    )
    res = assistant_service.process_message(req)
    assert res.intent == AssistantIntentEnum.SUPPORTED_LOCATION_QUERY
    assert res.tool_called == "get_supported_locations"
    assert res.tool_result["total_count"] == 81
