import json
import urllib.request
import urllib.error
import subprocess
import sys

BASE_URL = "http://localhost:8000"

def make_request(path, method="GET", data=None):
    url = f"{BASE_URL}{path}"
    headers = {"Accept": "application/json"}
    body = None
    if data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
    
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            resp_body = resp.read().decode("utf-8")
            return resp.status, json.loads(resp_body)
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8")
        try:
            parsed = json.loads(resp_body)
        except Exception:
            parsed = resp_body
        return e.code, parsed
    except Exception as e:
        return 0, str(e)

def run_all_checks():
    results = {}
    print("=" * 70)
    print("PHASE 5 COMPREHENSIVE REGRESSION & DETERMINISTIC INTEGRATION SUITE")
    print("=" * 70)

    # 1. Health Check
    status, data = make_request("/health")
    print(f"\n[1] /health => Status {status}")
    print(f"    Payload: {data}")
    health_pass = (
        status == 200 
        and data.get("status") in ["ok", "healthy"] 
        and data.get("model_loaded") is True 
        and data.get("locations_loaded") is True
        and data.get("v2_model_loaded") is True
    )
    results["health"] = "PASS" if health_pass else f"FAIL (status={status}, data={data})"
    print(f"    Health Result: {results['health']}")

    # 2. Locations Check
    status, data = make_request("/locations")
    locs = data.get("locations", []) if isinstance(data, dict) else []
    print(f"\n[2] /locations => Status {status}, total_locations: {len(locs)}")
    locs_pass = (status == 200 and len(locs) == 81 and data.get("total_locations") == 81)
    results["locations"] = "PASS" if locs_pass else f"FAIL (len={len(locs)})"
    print(f"    Locations Result: {results['locations']}")

    # 3. V1 Baseline Check (/predict)
    v1_payload = {
        "area_sqft": 1200,
        "bhk": 2,
        "bathroom": 2,
        "balcony": 1,
        "floor_num": 3,
        "total_floors": 10,
        "location": "bangalore",
        "Furnishing": "Semi-Furnished",
        "Transaction": "Resale",
        "facing": "East",
        "Ownership": "Freehold"
    }
    status, data = make_request("/predict", method="POST", data=v1_payload)
    print(f"\n[3] V1 /predict => Status {status}")
    print(f"    Payload: {data}")
    v1_pass = (
        status == 200 
        and "predicted_price" in data 
        and data.get("predicted_price_lakhs", 0) > 0
    )
    results["v1_predict"] = "PASS" if v1_pass else f"FAIL (status={status})"
    print(f"    V1 Predict Result: {results['v1_predict']}")

    # 4. V2 Bangalore Valid Case
    bangalore_payload = {
        "area_sqft": 1500,
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
    status, data = make_request("/api/v2/predict", method="POST", data=bangalore_payload)
    print(f"\n[4] V2 Bangalore => Status {status}")
    print(f"    Response: {data}")
    blr_pass = (
        status == 200 
        and data.get("status") == "success" 
        and data.get("predicted_price_lakhs", 0) > 0
        and data.get("engineered_features") is not None
    )
    results["v2_bangalore"] = "PASS" if blr_pass else f"FAIL (status={status})"
    print(f"    Bangalore Result: {results['v2_bangalore']}")

    # 5. V2 Mumbai Valid Case
    mumbai_payload = {
        "area_sqft": 1200,
        "bhk": 2,
        "latitude": 19.0760,
        "longitude": 72.8777,
        "city": "mumbai",
        "posted_by": "Owner",
        "rera": 1,
        "under_construction": 0,
        "ready_to_move": 1,
        "resale": 1,
        "is_rk": 0
    }
    status, data = make_request("/api/v2/predict", method="POST", data=mumbai_payload)
    print(f"\n[5] V2 Mumbai => Status {status}")
    print(f"    Response: {data}")
    mum_pass = (
        status == 200 
        and data.get("status") == "success" 
        and data.get("predicted_price_lakhs", 0) > 0
        and data.get("engineered_features") is not None
    )
    results["v2_mumbai"] = "PASS" if mum_pass else f"FAIL (status={status})"
    print(f"    Mumbai Result: {results['v2_mumbai']}")

    # 6. V2 Invalid Cases Matrix
    print("\n[6] Testing V2 Invalid Test Matrix (expecting 422 Unprocessable Entity)...")
    invalid_cases = [
        ("area <= 0", {**bangalore_payload, "area_sqft": 0}),
        ("area > 50000", {**bangalore_payload, "area_sqft": 55000}),
        ("BHK < 1", {**bangalore_payload, "bhk": 0}),
        ("BHK > 20", {**bangalore_payload, "bhk": 25}),
        ("invalid posted_by", {**bangalore_payload, "posted_by": "Unknown"}),
        ("lat out of range (< 6)", {**bangalore_payload, "latitude": 2.0}),
        ("lat out of range (> 38)", {**bangalore_payload, "latitude": 45.0}),
        ("lon out of range (< 68)", {**bangalore_payload, "longitude": 60.0}),
        ("lon out of range (> 98)", {**bangalore_payload, "longitude": 105.0}),
    ]

    invalid_results = []
    for label, payload in invalid_cases:
        status, data = make_request("/api/v2/predict", method="POST", data=payload)
        passed = (status == 422)
        invalid_results.append((label, status, passed, data))
        print(f"    - Case '{label}': HTTP {status} -> {'PASS (Correctly Rejected)' if passed else 'FAIL'}")

    all_invalid_pass = all(item[2] for item in invalid_results)
    results["v2_invalid_matrix"] = "PASS" if all_invalid_pass else "FAIL"

    print("\n" + "=" * 70)
    print("SUMMARY RESULTS:")
    for k, v in results.items():
        print(f"  {k}: {v}")
    print("=" * 70)

    return all(v == "PASS" for v in results.values())

if __name__ == "__main__":
    success = run_all_checks()
    if not success:
        sys.exit(1)
