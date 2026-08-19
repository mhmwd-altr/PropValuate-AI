import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.model_service import model_service
from backend.app.services.location_service import location_service

@pytest.fixture(scope="session", autouse=True)
def initialize_services():
    """Ensure model and location services are loaded for test session."""
    model_service.load()
    location_service.load()

@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as c:
        yield c
