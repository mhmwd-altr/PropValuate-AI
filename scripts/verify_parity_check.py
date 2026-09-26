import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import math
import joblib
import pandas as pd
import numpy as np
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.geo_service import (
    METRO_CENTERS as GEO_METROS,
    TOP_CITIES_V2,
    haversine_distance,
    normalize_city_group,
)
from backend.app.services.feature_service import feature_service, FEATURE_CONTRACT_V2
from scripts.train_valuation_v2 import METRO_CENTERS as TRAIN_METROS, haversine_distance as train_haversine

def run_parity_check():
    print("=" * 80)
    print("PHASE 4 FINAL — INFERENCE & ARCHITECTURE PARITY CHECK")
    print("=" * 80)

    # 1. Inspect Trained Model Artifact
    model_v2 = joblib.load("backend/models/house_price_v2.pkl")
    preprocessor = model_v2.named_steps["preprocessor"]
    cat_trans = preprocessor.named_transformers_["cat"]
    trained_categories = [list(c) for c in cat_trans.categories_]
    trained_posted_by = trained_categories[0]
    trained_city_grouped = set(trained_categories[1])

    print("\n--- 1. CITY & CATEGORY PARITY CHECK ---")
    print(f"Trained posted_by categories ({len(trained_posted_by)}): {trained_posted_by}")
    print(f"Trained city_grouped categories ({len(trained_city_grouped)}): {sorted(trained_city_grouped)}")
    print(f"Backend TOP_CITIES_V2 count: {len(TOP_CITIES_V2)} (with 'other': {len(TOP_CITIES_V2) + 1})")

    backend_categories_with_other = set(TOP_CITIES_V2) | {"other"}
    diff_trained_minus_backend = trained_city_grouped - backend_categories_with_other
    diff_backend_minus_trained = backend_categories_with_other - trained_city_grouped

    print(f"Discrepancy (Trained - Backend): {diff_trained_minus_backend if diff_trained_minus_backend else 'None (0)'}")
    print(f"Discrepancy (Backend - Trained): {diff_backend_minus_trained if diff_backend_minus_trained else 'None (0)'}")
    cat_match = (trained_city_grouped == backend_categories_with_other)
    print(f"Categories Match Perfectly: {cat_match}")
    assert cat_match, "Category mismatch between training artifact and backend mapping!"

    # 2. Geospatial Constant & Formula Parity Check
    print("\n--- 2. GEOSPATIAL PARITY CHECK ---")
    metros_match = (GEO_METROS == TRAIN_METROS)
    print(f"Metro Coordinates Match: {metros_match}")
    for m, coords in GEO_METROS.items():
        print(f"  {m:12s}: Training={TRAIN_METROS[m]} | Inference={coords} | Match={TRAIN_METROS[m] == coords}")
    assert metros_match, "Metro coordinate mismatch!"

    # Test sample coordinates distance
    test_lat, test_lon = 12.9716, 77.5946
    dist_train = train_haversine(test_lat, test_lon, TRAIN_METROS["mumbai"][0], TRAIN_METROS["mumbai"][1])
    dist_infer = haversine_distance(test_lat, test_lon, GEO_METROS["mumbai"][0], GEO_METROS["mumbai"][1])
    dist_diff = abs(dist_train - dist_infer)
    print(f"\nHaversine Formula Output Match (Bangalore -> Mumbai):")
    print(f"  Training Function:  {dist_train:.8f} km")
    print(f"  Inference Function: {dist_infer:.8f} km")
    print(f"  Absolute Diff:      {dist_diff:.12f} km")
    assert dist_diff < 1e-6, "Haversine formula calculation difference detected!"

    # 3. Direct Inference vs API Inference Parity
    print("\n--- 3. DIRECT INFERENCE VS API PARITY ---")
    samples = [
        {
            "name": "Bangalore Central Apartment",
            "payload": {
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
        },
        {
            "name": "Mumbai South Luxury Flat",
            "payload": {
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
        },
        {
            "name": "Delhi-NCR Gurgaon Builder Floor",
            "payload": {
                "area_sqft": 1800.0,
                "bhk": 3,
                "latitude": 28.4595,
                "longitude": 77.0266,
                "city": "gurgaon",
                "posted_by": "Dealer",
                "rera": 1,
                "under_construction": 1,
                "ready_to_move": 0,
                "resale": 0,
                "is_rk": 0
            }
        },
        {
            "name": "Unobserved Tier-2 Municipality (Tirupati)",
            "payload": {
                "area_sqft": 1400.0,
                "bhk": 3,
                "latitude": 13.6288,
                "longitude": 79.4192,
                "city": "tirupati",
                "posted_by": "Owner",
                "rera": 1,
                "under_construction": 0,
                "ready_to_move": 1,
                "resale": 1,
                "is_rk": 0
            }
        }
    ]

    all_passed = True
    with TestClient(app) as client:
        for s in samples:
            name = s["name"]
            payload = s["payload"]
            
            # A. Direct Inference
            feat_dict = feature_service.construct_v2_features(payload)
            df_direct = feature_service.to_dataframe(feat_dict)
            pred_direct_raw = float(model_v2.predict(df_direct)[0])
            pred_direct_lakhs = round(pred_direct_raw / 100000.0, 2)
            
            # B. API Inference
            resp = client.post("/api/v2/predict", json=payload)
            assert resp.status_code == 200, f"API failed with status {resp.status_code}"
            resp_data = resp.json()
            pred_api_raw = resp_data["predicted_price"]
            pred_api_lakhs = resp_data["predicted_price_lakhs"]
            
            diff_inr = abs(pred_direct_raw - pred_api_raw)
            diff_lakhs = abs(pred_direct_lakhs - pred_api_lakhs)
            
            verdict = "EXACT MATCH (PASS)" if diff_inr < 0.01 else "MISMATCH (FAIL)"
            if diff_inr >= 0.01:
                all_passed = False
                
            print(f"\nSample: {name}")
            print(f"  Inputs:        {payload['area_sqft']} sqft, {payload['bhk']} BHK, Lat={payload['latitude']}, Lon={payload['longitude']}, City={payload['city']}")
            print(f"  Direct V2:     Rs {pred_direct_raw:,.2f} ({pred_direct_lakhs:.2f} Lakhs)")
            print(f"  API V2:        Rs {pred_api_raw:,.2f} ({pred_api_lakhs:.2f} Lakhs)")
            print(f"  Diff INR:      Rs {diff_inr:.6f}")
            print(f"  Diff Lakhs:    {diff_lakhs:.6f}")
            print(f"  Verdict:       {verdict}")

    print("\n" + "=" * 80)
    print(f"ALL PARITY CHECKS: {'PASS' if all_passed else 'FAIL'}")
    print("=" * 80)

if __name__ == "__main__":
    run_parity_check()
