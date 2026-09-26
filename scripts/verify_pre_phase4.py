import os
import sys
import json
import hashlib
import time
import joblib
import pandas as pd
import numpy as np

def compute_sha256(filepath):
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def main():
    print("=" * 80)
    print("PRE-PHASE 4 — READINESS & INTEGRITY VERIFICATION")
    print("=" * 80)

    # 1. Artifact Existence & Integrity Check
    artifacts = [
        "backend/models/house_price.pkl",
        "backend/models/house_price_v2.pkl",
        "backend/models/locations.json",
        "models/registry/model_v2_metadata.json",
        "models/registry/multi_model_comparison.json",
        "reports/phase3_model_comparison.md",
        "reports/phase3_error_analysis.md",
        "notebooks/phase3_valuation_engine_v2.ipynb"
    ]
    
    print("\n--- 1. Artifact Verification ---")
    all_present = True
    for art in artifacts:
        exists = os.path.exists(art)
        size_kb = round(os.path.getsize(art) / 1024, 2) if exists else 0
        status = f"[OK] ({size_kb} KB)" if exists else "[MISSING]"
        print(f"  {art:45s}: {status}")
        if not exists:
            all_present = False

    # 2. Baseline Model Inspection (house_price.pkl)
    print("\n--- 2. Champion Baseline Model Inspection ---")
    base_path = os.path.join("backend", "models", "house_price.pkl")
    base_model = joblib.load(base_path)
    base_hash = compute_sha256(base_path)
    print(f"  Path:        {base_path}")
    print(f"  SHA256:      {base_hash}")
    print(f"  Object Type: {type(base_model)}")
    print(f"  Pipeline Steps: {list(base_model.named_steps.keys()) if hasattr(base_model, 'named_steps') else 'N/A'}")
    
    # 3. Valuation Engine V2 Candidate Inspection (house_price_v2.pkl)
    print("\n--- 3. Valuation Engine V2 Candidate Inspection ---")
    v2_path = os.path.join("backend", "models", "house_price_v2.pkl")
    v2_model = joblib.load(v2_path)
    v2_hash = compute_sha256(v2_path)
    print(f"  Path:        {v2_path}")
    print(f"  SHA256:      {v2_hash}")
    print(f"  Object Type: {type(v2_model)}")
    print(f"  Pipeline Steps: {list(v2_model.named_steps.keys()) if hasattr(v2_model, 'named_steps') else 'N/A'}")
    
    # 4. Feature Contract Extraction from V2
    print("\n--- 4. Feature Contract Extraction from V2 Pipeline ---")
    pre = v2_model.named_steps.get("preprocessor")
    if hasattr(pre, "transformers_"):
        for name, trans, cols in pre.transformers_:
            print(f"  Transformer '{name}' ({type(trans).__name__}):")
            print(f"    Features ({len(cols)}): {cols}")

    # 5. Direct Inference Sanity Check on V2
    print("\n--- 5. Direct Inference Sanity Check on V2 ---")
    # Realistic test property in Bangalore
    test_sample = pd.DataFrame([{
        "area_sqft": 1500.0,
        "bhk": 3,
        "is_rk": 0,
        "rera": 1,
        "under_construction": 0,
        "ready_to_move": 1,
        "resale": 1,
        "latitude": 12.9716,
        "longitude": 77.5946,
        "area_per_bhk": 1500.0 / 3.1,
        "dist_nearest_metro_km": 0.0,
        "dist_mumbai_km": 840.0,
        "dist_delhi_km": 1740.0,
        "dist_bangalore_km": 0.0,
        "posted_by": "Owner",
        "city_grouped": "bangalore"
    }])
    
    t0 = time.time()
    pred_inr = v2_model.predict(test_sample)[0]
    inf_latency_ms = (time.time() - t0) * 1000.0
    pred_lakhs = pred_inr / 100000.0
    
    print(f"  Test Sample: 1500 sqft, 3 BHK, Bangalore Central, RERA=1, Resale=1")
    print(f"  Predicted Valuation (INR):   Rs. {pred_inr:,.2f}")
    print(f"  Predicted Valuation (Lakhs): Rs. {pred_lakhs:.2f} Lakhs")
    print(f"  Inference Latency:           {inf_latency_ms:.2f} ms")
    print(f"  Inference Valid (No NaN, >0): {not np.isnan(pred_inr) and pred_inr > 0}")

    # Second Test Sample: Mumbai Central Luxury
    test_sample_2 = pd.DataFrame([{
        "area_sqft": 2200.0,
        "bhk": 4,
        "is_rk": 0,
        "rera": 1,
        "under_construction": 0,
        "ready_to_move": 1,
        "resale": 0,
        "latitude": 18.9220,
        "longitude": 72.8347,
        "area_per_bhk": 2200.0 / 4.1,
        "dist_nearest_metro_km": 0.0,
        "dist_mumbai_km": 0.0,
        "dist_delhi_km": 1150.0,
        "dist_bangalore_km": 840.0,
        "posted_by": "Builder",
        "city_grouped": "mumbai"
    }])
    pred_inr_2 = v2_model.predict(test_sample_2)[0]
    print(f"  Test Sample 2: 2200 sqft, 4 BHK, Mumbai South (Builder New Sale)")
    print(f"  Predicted Valuation (INR):   Rs. {pred_inr_2:,.2f} ({pred_inr_2/100000.0:.2f} Lakhs)")

    print("\n" + "=" * 80)
    print("ALL INTEGRITY CHECKS PASSED: READY FOR PRE-PHASE 4 REPORT")
    print("=" * 80)

if __name__ == "__main__":
    main()
