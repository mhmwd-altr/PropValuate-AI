import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.assistant_service import assistant_service
from backend.app.services.language_providers.mock_provider import MockLanguageProvider

@pytest.fixture(autouse=True)
def setup_api_test():
    assistant_service._provider = MockLanguageProvider()

client = TestClient(app)

def test_api_assistant_chat_endpoint():
    response = client.post(
        "/api/v2/assistant",
        json={"message": "I want to estimate price for 1200 sqft 2 BHK in Pune."}
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["intent"] == "VALUATION_REQUEST"
    assert data["is_valuation_complete"] is True
    assert data["tool_called"] == "predict_property_price"
    assert data["tool_result"]["predicted_price_lakhs"] > 0

def test_api_assistant_clarification_endpoint():
    response = client.post(
        "/api/v2/assistant",
        json={"message": "I have an apartment."}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "PROPERTY_INPUT_CLARIFICATION"
    assert data["is_valuation_complete"] is False
    assert len(data["missing_slots"]) > 0

def test_api_assistant_reset_endpoint():
    # Chat first to create session
    chat_res = client.post(
        "/api/v2/assistant",
        json={"message": "1500 sqft 3 BHK in Bangalore"}
    )
    session_id = chat_res.json()["session_id"]

    # Reset session
    reset_res = client.post(f"/api/v2/assistant/reset?session_id={session_id}")
    assert reset_res.status_code == 200
    assert reset_res.json()["status"] == "reset_success"

def test_api_assistant_health_endpoint():
    res = client.get("/api/v2/assistant/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "model_path" in data

def test_api_assistant_empty_message_validation():
    response = client.post(
        "/api/v2/assistant",
        json={"message": "   "}
    )
    assert response.status_code == 422
