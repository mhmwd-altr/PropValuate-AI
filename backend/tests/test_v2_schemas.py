import pytest
from pydantic import ValidationError
from backend.app.schemas.prediction_v2 import (
    PredictionRequestV2,
    PredictionResponseV2,
    EngineeredFeaturesMetadata,
)

def test_valid_v2_prediction_request():
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
    req = PredictionRequestV2(**payload)
    assert req.area_sqft == 1500.0
    assert req.bhk == 3
    assert req.latitude == 12.9716
    assert req.longitude == 77.5946
    assert req.city == "bangalore"
    assert req.posted_by == "Owner"
    assert req.rera == 1
    assert req.under_construction == 0
    assert req.ready_to_move == 1
    assert req.resale == 1
    assert req.is_rk == 0

def test_v2_prediction_request_defaults():
    payload = {
        "area_sqft": 1200.0,
        "bhk": 2,
        "latitude": 19.0760,
        "longitude": 72.8777
    }
    req = PredictionRequestV2(**payload)
    assert req.city == "other"
    assert req.posted_by == "Owner"
    assert req.rera == 1
    assert req.under_construction == 0
    assert req.ready_to_move == 1
    assert req.resale == 1
    assert req.is_rk == 0

def test_v2_prediction_request_missing_required_latitude():
    payload = {
        "area_sqft": 1200.0,
        "bhk": 2,
        "longitude": 72.8777
    }
    with pytest.raises(ValidationError) as exc:
        PredictionRequestV2(**payload)
    assert "latitude" in str(exc.value)

def test_v2_prediction_request_missing_required_area():
    payload = {
        "bhk": 2,
        "latitude": 19.0760,
        "longitude": 72.8777
    }
    with pytest.raises(ValidationError) as exc:
        PredictionRequestV2(**payload)
    assert "area_sqft" in str(exc.value)

def test_v2_prediction_request_invalid_area_bounds():
    # Negative area
    with pytest.raises(ValidationError):
        PredictionRequestV2(area_sqft=-100.0, bhk=2, latitude=12.97, longitude=77.59)
    
    # Zero area
    with pytest.raises(ValidationError):
        PredictionRequestV2(area_sqft=0.0, bhk=2, latitude=12.97, longitude=77.59)
        
    # Unrealistically huge area (>50000 sqft)
    with pytest.raises(ValidationError):
        PredictionRequestV2(area_sqft=100000.0, bhk=2, latitude=12.97, longitude=77.59)

def test_v2_prediction_request_invalid_bhk_bounds():
    # Zero BHK
    with pytest.raises(ValidationError):
        PredictionRequestV2(area_sqft=1000.0, bhk=0, latitude=12.97, longitude=77.59)
    
    # Negative BHK
    with pytest.raises(ValidationError):
        PredictionRequestV2(area_sqft=1000.0, bhk=-1, latitude=12.97, longitude=77.59)
        
    # BHK > 20
    with pytest.raises(ValidationError):
        PredictionRequestV2(area_sqft=1000.0, bhk=25, latitude=12.97, longitude=77.59)

def test_v2_prediction_request_latitude_bounds():
    # Latitude too far south (<6.0)
    with pytest.raises(ValidationError) as exc:
        PredictionRequestV2(area_sqft=1000.0, bhk=2, latitude=2.5, longitude=77.59)
    assert "latitude" in str(exc.value)

    # Latitude too far north (>38.0)
    with pytest.raises(ValidationError) as exc:
        PredictionRequestV2(area_sqft=1000.0, bhk=2, latitude=45.0, longitude=77.59)
    assert "latitude" in str(exc.value)

def test_v2_prediction_request_longitude_bounds():
    # Longitude too far west (<68.0)
    with pytest.raises(ValidationError) as exc:
        PredictionRequestV2(area_sqft=1000.0, bhk=2, latitude=12.97, longitude=50.0)
    assert "longitude" in str(exc.value)

    # Longitude too far east (>98.0)
    with pytest.raises(ValidationError) as exc:
        PredictionRequestV2(area_sqft=1000.0, bhk=2, latitude=12.97, longitude=110.0)
    assert "longitude" in str(exc.value)

def test_v2_prediction_request_posted_by_normalization():
    # Case insensitivity
    req = PredictionRequestV2(area_sqft=1000.0, bhk=2, latitude=12.97, longitude=77.59, posted_by="dealer")
    assert req.posted_by == "Dealer"
    
    req2 = PredictionRequestV2(area_sqft=1000.0, bhk=2, latitude=12.97, longitude=77.59, posted_by="BUILDER")
    assert req2.posted_by == "Builder"

    # Invalid posted_by
    with pytest.raises(ValidationError) as exc:
        PredictionRequestV2(area_sqft=1000.0, bhk=2, latitude=12.97, longitude=77.59, posted_by="UnknownAgent")
    assert "posted_by" in str(exc.value)

def test_v2_prediction_request_binary_flags():
    # Invalid rera (>1)
    with pytest.raises(ValidationError):
        PredictionRequestV2(area_sqft=1000.0, bhk=2, latitude=12.97, longitude=77.59, rera=5)
        
    # Invalid resale (<0)
    with pytest.raises(ValidationError):
        PredictionRequestV2(area_sqft=1000.0, bhk=2, latitude=12.97, longitude=77.59, resale=-1)

def test_v2_prediction_response_schema():
    meta = EngineeredFeaturesMetadata(
        area_per_bhk=483.87,
        dist_nearest_metro_km=0.0,
        dist_mumbai_km=841.4,
        dist_delhi_km=1740.2,
        dist_bangalore_km=0.0,
        city_grouped="bangalore"
    )
    resp = PredictionResponseV2(
        status="success",
        predicted_price=9236394.38,
        predicted_price_lakhs=92.36,
        currency="INR",
        model_version="2.0.0",
        model_name="Valuation Engine V2 (HistGradientBoosting)",
        engineered_features=meta
    )
    assert resp.status == "success"
    assert resp.predicted_price == 9236394.38
    assert resp.predicted_price_lakhs == 92.36
    assert resp.engineered_features.city_grouped == "bangalore"
    assert resp.engineered_features.area_per_bhk == 483.87
