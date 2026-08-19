import pytest
from fastapi.testclient import TestClient

def test_get_locations_success(client: TestClient):
    response = client.get("/locations")
    assert response.status_code == 200
    data = response.json()
    assert "total_locations" in data
    assert "locations" in data
    assert isinstance(data["locations"], list)
    assert data["total_locations"] == len(data["locations"])
    assert data["total_locations"] == 81

def test_known_cities_in_locations(client: TestClient):
    response = client.get("/locations")
    assert response.status_code == 200
    locations = response.json()["locations"]
    
    expected_cities = [
        "bangalore",
        "mumbai",
        "new-delhi",
        "gurgaon",
        "chennai",
        "hyderabad",
        "kolkata",
        "pune",
        "ahmedabad",
        "jaipur"
    ]
    for city in expected_cities:
        assert city in locations, f"Expected city '{city}' not found in locations list!"
