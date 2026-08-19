import pytest
from fastapi.testclient import TestClient

def test_predict_valid_property(client: TestClient):
    payload = {
        "area_sqft": 1500.0,
        "bhk": 3,
        "bathroom": 2.0,
        "balcony": 2.0,
        "floor_num": 4.0,
        "total_floors": 10.0,
        "location": "bangalore",
        "Furnishing": "Semi-Furnished",
        "Transaction": "Resale",
        "facing": "East",
        "Ownership": "Freehold"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_price" in data
    assert "predicted_price_lakhs" in data
    assert data["predicted_price"] > 0
    assert data["predicted_price_lakhs"] > 0
    assert data["currency"] == "INR"
    assert data["status"] == "success"
    assert round(data["predicted_price"] / 100000.0, 2) == data["predicted_price_lakhs"]

def test_predict_with_default_optional_fields(client: TestClient):
    payload = {
        "area_sqft": 1000.0,
        "bhk": 2,
        "bathroom": 2.0,
        "location": "mumbai"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_price"] > 0
    assert data["status"] == "success"

def test_predict_missing_required_area(client: TestClient):
    payload = {
        "bhk": 3,
        "bathroom": 2.0,
        "location": "bangalore"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()

def test_predict_missing_required_location(client: TestClient):
    payload = {
        "area_sqft": 1200.0,
        "bhk": 2,
        "bathroom": 2.0
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

def test_predict_invalid_negative_area(client: TestClient):
    payload = {
        "area_sqft": -500.0,
        "bhk": 2,
        "bathroom": 2.0,
        "location": "bangalore"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

def test_predict_invalid_zero_bhk(client: TestClient):
    payload = {
        "area_sqft": 1200.0,
        "bhk": 0,
        "bathroom": 2.0,
        "location": "bangalore"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

def test_predict_floor_exceeds_total_floors(client: TestClient):
    payload = {
        "area_sqft": 1500.0,
        "bhk": 3,
        "bathroom": 2.0,
        "balcony": 1.0,
        "floor_num": 15.0,
        "total_floors": 5.0,
        "location": "bangalore"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
    error_detail = response.json()["detail"]
    assert any("cannot exceed total_floors" in str(err) for err in error_detail)

def test_predict_unseen_categorical_handling(client: TestClient):
    payload = {
        "area_sqft": 1100.0,
        "bhk": 2,
        "bathroom": 2.0,
        "balcony": 1.0,
        "floor_num": 2.0,
        "total_floors": 5.0,
        "location": "unknown_future_city",
        "Furnishing": "UnknownType",
        "Transaction": "UnknownTx",
        "facing": "UnknownFacing",
        "Ownership": "UnknownOwnership"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_price"] > 0
    assert data["status"] == "success"
