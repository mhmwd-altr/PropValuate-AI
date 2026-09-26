import time
import pytest
from fastapi.testclient import TestClient

def test_v2_predict_golden_bangalore_sample(client: TestClient):
    """
    Golden Test Case 1: Bangalore Central Standard Apartment
    1500 sqft, 3 BHK, Owner, Resale, RERA Approved
    """
    payload = {
        "area_sqft": 1500.0,
        "bhk": 3,
        "latitude": 12.9716,
        "longitude": 77.5946,
        "city": "bangalore",
        "posted_by": "Owner",
        "rera": 1,
        "under_construction": 0,
        "ready_to_move": 1,
        "resale": 1,
        "is_rk": 0
    }
    t0 = time.time()
    response = client.post("/api/v2/predict", json=payload)
    latency_ms = (time.time() - t0) * 1000.0
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["currency"] == "INR"
    assert data["model_version"] == "2.0.0"
    
    # Valuation check: approximately Rs. 92.36 Lakhs (+/- 10%)
    assert 80.0 <= data["predicted_price_lakhs"] <= 110.0
    assert data["predicted_price"] > 0
    assert round(data["predicted_price"] / 100000.0, 2) == data["predicted_price_lakhs"]
    
    # Check engineered features in response metadata
    meta = data["engineered_features"]
    assert meta["city_grouped"] == "bangalore"
    assert meta["dist_bangalore_km"] == 0.0
    assert meta["dist_nearest_metro_km"] == 0.0
    assert meta["dist_mumbai_km"] > 800.0
    assert meta["dist_delhi_km"] > 1700.0
    assert round(meta["area_per_bhk"], 1) == round(1500.0 / 3.1, 1)
    
    # Latency sanity check (< 200 ms)
    assert latency_ms < 200.0

def test_v2_predict_golden_mumbai_luxury_sample(client: TestClient):
    """
    Golden Test Case 2: Mumbai South Luxury Flat
    2200 sqft, 4 BHK, Builder Primary Sale, RERA Approved
    """
    payload = {
        "area_sqft": 2200.0,
        "bhk": 4,
        "latitude": 18.9220,
        "longitude": 72.8347,
        "city": "mumbai",
        "posted_by": "Builder",
        "rera": 1,
        "under_construction": 0,
        "ready_to_move": 1,
        "resale": 0,
        "is_rk": 0
    }
    response = client.post("/api/v2/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["predicted_price_lakhs"] > 300.0  # Luxury Mumbai South pricing
    assert data["engineered_features"]["city_grouped"] == "mumbai"
    assert data["engineered_features"]["dist_mumbai_km"] == 0.0

def test_v2_predict_with_default_optional_fields(client: TestClient):
    """Verifies that client can submit minimal raw inputs."""
    payload = {
        "area_sqft": 1100.0,
        "bhk": 2,
        "latitude": 13.0827,
        "longitude": 80.2707,
        "city": "chennai"
    }
    response = client.post("/api/v2/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["predicted_price"] > 0
    assert data["engineered_features"]["city_grouped"] == "chennai"

def test_v2_predict_rk_studio_layout(client: TestClient):
    """Verifies RK studio property valuation."""
    payload = {
        "area_sqft": 450.0,
        "bhk": 1,
        "latitude": 12.9716,
        "longitude": 77.5946,
        "city": "bangalore",
        "is_rk": 1
    }
    response = client.post("/api/v2/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_price_lakhs"] > 0
    assert data["predicted_price_lakhs"] < 50.0  # Realistic for 450 sqft RK

def test_v2_predict_unobserved_municipality(client: TestClient):
    """Verifies continuous geospatial generalization on unobserved tier-2/3 town."""
    payload = {
        "area_sqft": 1400.0,
        "bhk": 3,
        "latitude": 13.6288,
        "longitude": 79.4192,
        "city": "Tirupati"  # Not in top 50, mapped to 'other'
    }
    response = client.post("/api/v2/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["predicted_price_lakhs"] > 0
    assert data["engineered_features"]["city_grouped"] == "other"
    assert data["engineered_features"]["dist_nearest_metro_km"] > 0

def test_v2_predict_missing_latitude_422(client: TestClient):
    payload = {
        "area_sqft": 1200.0,
        "bhk": 2,
        "longitude": 77.5946
    }
    response = client.post("/api/v2/predict", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()

def test_v2_predict_out_of_bounds_latitude_422(client: TestClient):
    # London latitude (51.5074)
    payload = {
        "area_sqft": 1200.0,
        "bhk": 2,
        "latitude": 51.5074,
        "longitude": 77.5946
    }
    response = client.post("/api/v2/predict", json=payload)
    assert response.status_code == 422

def test_v2_predict_out_of_bounds_longitude_422(client: TestClient):
    # Outside India longitude (-0.1278)
    payload = {
        "area_sqft": 1200.0,
        "bhk": 2,
        "latitude": 12.9716,
        "longitude": -0.1278
    }
    response = client.post("/api/v2/predict", json=payload)
    assert response.status_code == 422

def test_v2_predict_negative_area_422(client: TestClient):
    payload = {
        "area_sqft": -800.0,
        "bhk": 2,
        "latitude": 12.9716,
        "longitude": 77.5946
    }
    response = client.post("/api/v2/predict", json=payload)
    assert response.status_code == 422

def test_health_reports_both_models_loaded(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True
    assert data["v2_model_loaded"] is True
    assert data["locations_loaded"] is True
    assert data["version"] == "1.0.0"

def test_root_lists_v2_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "endpoints" in data
    assert data["endpoints"]["predict"] == "/predict"
    assert data["endpoints"]["predict_v2"] == "/api/v2/predict"
