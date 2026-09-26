import pytest
from backend.app.services.capability_router import capability_router
from backend.app.schemas.assistant import PropertySlots
from backend.app.services.model_service_v2 import model_service_v2
from backend.app.services.location_service import location_service

@pytest.fixture(autouse=True)
def ensure_models_loaded():
    if not model_service_v2.is_loaded:
        model_service_v2.load()
    if not location_service.is_loaded:
        location_service.load()

def test_capability_router_predict_property_price_success():
    slots = PropertySlots(
        area_sqft=1500.0,
        bhk=3,
        city="bangalore",
        posted_by="Owner",
        rera=1,
        under_construction=0,
        ready_to_move=1,
        resale=1,
        is_rk=0
    )
    result = capability_router.execute_tool("predict_property_price", slots=slots)
    assert result.status == "success"
    assert result.tool_name == "predict_property_price"
    assert result.data is not None
    assert result.data["predicted_price"] > 0
    assert result.data["predicted_price_lakhs"] > 0
    assert result.data["rate_per_sqft"] > 0
    assert result.data["model_version"] == "2.0.0"

def test_capability_router_missing_mandatory_slots():
    slots = PropertySlots(area_sqft=1500.0, bhk=None, city="bangalore")
    result = capability_router.execute_tool("predict_property_price", slots=slots)
    assert result.status == "incomplete"
    assert "bhk" in result.error

def test_capability_router_unsupported_city():
    slots = PropertySlots(area_sqft=1500.0, bhk=3, city="london")
    result = capability_router.execute_tool("predict_property_price", slots=slots)
    assert result.status == "unsupported_location"
    assert "london" in result.error.lower()

def test_capability_router_get_supported_locations():
    result = capability_router.execute_tool("get_supported_locations")
    assert result.status == "success"
    assert result.data["total_count"] == 81
    assert "bangalore" in result.data["locations"]
    assert "mumbai" in result.data["locations"]

def test_capability_router_reject_arbitrary_tool():
    result = capability_router.execute_tool("arbitrary_exec_tool", slots=None)
    assert result.status == "error"
    assert "not authorized" in result.error
