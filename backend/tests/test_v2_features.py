import pytest
import math
import pandas as pd
from backend.app.services.geo_service import (
    haversine_distance,
    is_valid_india_coordinate,
    calculate_metro_distances,
    normalize_city_group,
    METRO_CENTERS,
    TOP_CITIES_V2,
)
from backend.app.services.feature_service import (
    feature_service,
    FEATURE_CONTRACT_V2,
    NUMERICAL_FEATURES_V2,
    CATEGORICAL_FEATURES_V2,
)

def test_haversine_distance_accuracy():
    # Distance between identical points must be 0
    d_zero = haversine_distance(12.9716, 77.5946, 12.9716, 77.5946)
    assert d_zero == 0.0

    # Distance between Mumbai and Bangalore is approx 834.55 km (+/- 5 km)
    mumbai_lat, mumbai_lon = METRO_CENTERS["mumbai"]
    bng_lat, bng_lon = METRO_CENTERS["bangalore"]
    d_mum_bng = haversine_distance(mumbai_lat, mumbai_lon, bng_lat, bng_lon)
    assert 830.0 < d_mum_bng < 845.0

    # Distance between Delhi and Bangalore is approx 1740 km (+/- 10 km)
    delhi_lat, delhi_lon = METRO_CENTERS["delhi"]
    d_del_bng = haversine_distance(delhi_lat, delhi_lon, bng_lat, bng_lon)
    assert 1730.0 < d_del_bng < 1755.0

def test_coordinate_validation():
    # Valid Indian coordinates
    assert is_valid_india_coordinate(12.9716, 77.5946) is True  # Bangalore
    assert is_valid_india_coordinate(28.6304, 77.2177) is True  # Delhi
    assert is_valid_india_coordinate(18.9220, 72.8347) is True  # Mumbai
    assert is_valid_india_coordinate(22.5726, 88.3639) is True  # Kolkata
    assert is_valid_india_coordinate(6.0, 68.0) is True         # Min boundary
    assert is_valid_india_coordinate(38.0, 98.0) is True        # Max boundary

    # Invalid coordinates (outside India)
    assert is_valid_india_coordinate(51.5074, -0.1278) is False  # London
    assert is_valid_india_coordinate(40.7128, -74.0060) is False # New York
    assert is_valid_india_coordinate(-33.8688, 151.2093) is False# Sydney
    assert is_valid_india_coordinate(5.9, 77.0) is False         # Lat < 6.0
    assert is_valid_india_coordinate(38.1, 77.0) is False        # Lat > 38.0
    assert is_valid_india_coordinate(20.0, 67.9) is False        # Lon < 68.0
    assert is_valid_india_coordinate(20.0, 98.1) is False        # Lon > 98.0
    assert is_valid_india_coordinate(float("nan"), 77.0) is False
    assert is_valid_india_coordinate(20.0, float("inf")) is False

def test_calculate_metro_distances():
    # In Bangalore core
    bng_lat, bng_lon = METRO_CENTERS["bangalore"]
    dists = calculate_metro_distances(bng_lat, bng_lon)
    assert dists["dist_bangalore_km"] == 0.0
    assert dists["dist_nearest_metro_km"] == 0.0
    assert dists["dist_mumbai_km"] > 800.0
    assert dists["dist_delhi_km"] > 1700.0

    # In Mumbai core
    mum_lat, mum_lon = METRO_CENTERS["mumbai"]
    dists_mum = calculate_metro_distances(mum_lat, mum_lon)
    assert dists_mum["dist_mumbai_km"] == 0.0
    assert dists_mum["dist_nearest_metro_km"] == 0.0

def test_city_group_normalization():
    # Known top cities
    assert normalize_city_group("bangalore") == "bangalore"
    assert normalize_city_group("mumbai") == "mumbai"
    assert normalize_city_group("chennai") == "chennai"
    assert normalize_city_group("kolkata") == "kolkata"
    assert normalize_city_group("gurgaon") == "gurgaon"
    assert normalize_city_group("agra") == "agra"

    # Case & whitespace handling
    assert normalize_city_group("   BANGALORE  ") == "bangalore"
    assert normalize_city_group("MuMbAi") == "mumbai"

    # Aliases
    assert normalize_city_group("Bengaluru") == "bangalore"
    assert normalize_city_group("Bombay") == "mumbai"
    assert normalize_city_group("Gurugram") == "gurgaon"
    assert normalize_city_group("Calcutta") == "kolkata"
    assert normalize_city_group("Madras") == "chennai"
    assert normalize_city_group("Cochin") == "kochi"

    # Rare / unobserved municipalities default to 'other'
    assert normalize_city_group("random_village_xyz") == "other"
    assert normalize_city_group("tirupati") == "other"
    assert normalize_city_group("udaipur") == "other"
    assert normalize_city_group("") == "other"
    assert normalize_city_group(None) == "other"

def test_construct_v2_features():
    raw_sample = {
        "area_sqft": 1500.0,
        "bhk": 3,
        "latitude": 12.9716,
        "longitude": 77.5946,
        "city": "Bengaluru",
        "posted_by": "owner",
        "rera": 1,
        "under_construction": 0,
        "ready_to_move": 1,
        "resale": 1,
        "is_rk": 0
    }
    features = feature_service.construct_v2_features(raw_sample)
    
    # Verify all 16 keys exist
    for col in FEATURE_CONTRACT_V2:
        assert col in features, f"Missing feature '{col}' in output!"
        
    assert features["area_sqft"] == 1500.0
    assert features["bhk"] == 3
    assert features["area_per_bhk"] == round(1500.0 / 3.1, 4)
    assert features["posted_by"] == "Owner"
    assert features["city_grouped"] == "bangalore"
    assert features["dist_bangalore_km"] == 0.0
    assert features["dist_nearest_metro_km"] == 0.0
    assert features["rera"] == 1
    assert features["resale"] == 1

def test_feature_service_to_dataframe():
    raw_sample = {
        "area_sqft": 2000.0,
        "bhk": 4,
        "latitude": 18.9220,
        "longitude": 72.8347,
        "city": "mumbai",
        "posted_by": "Builder",
        "rera": 1,
        "under_construction": 1,
        "ready_to_move": 0,
        "resale": 0,
        "is_rk": 0
    }
    features = feature_service.construct_v2_features(raw_sample)
    df = feature_service.to_dataframe(features)
    
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (1, 16)
    assert list(df.columns) == FEATURE_CONTRACT_V2
    assert df["posted_by"].iloc[0] == "Builder"
    assert df["city_grouped"].iloc[0] == "mumbai"

def test_feature_construction_invalid_coords_raises():
    invalid_sample = {
        "area_sqft": 1500.0,
        "bhk": 3,
        "latitude": 51.5074,  # London
        "longitude": -0.1278,
    }
    with pytest.raises(ValueError) as exc:
        feature_service.construct_v2_features(invalid_sample)
    assert "outside valid India bounding box" in str(exc.value)
