import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.model_service import model_service
from backend.app.services.model_service_v2 import model_service_v2
from backend.app.services.location_service import location_service

@pytest.fixture(scope="session", autouse=True)
def initialize_services():
    """Ensure baseline model, V2 model, and location services are loaded for test session."""
    model_service.load()
    model_service_v2.load()
    location_service.load()

@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as c:
        yield c
