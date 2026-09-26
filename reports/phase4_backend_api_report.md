# PropValuate AI — Phase 4 Backend Foundation & API Contracts Report

**Project:** PropValuate AI — India Real-Estate Intelligence Platform  
**Stage:** Phase 4 — Backend Foundation & API Contracts  
**Status:** PASS — Complete & Verified  
**Date:** September 2026  
**Author / Agent:** PropValuate AI Implementation Agent  

---

## 1. Current Backend Architecture

The backend is built with FastAPI (Python 3.11) and follows a decoupled, modular service-oriented architecture designed to scale with future multimodal features (Language, Vision, Market Intelligence) while maintaining 100% backward compatibility with the protected baseline.

```text
                                FastAPI Application Core (main.py)
                                                │
                 ┌──────────────────────────────┴──────────────────────────────┐
                 ▼                                                             ▼
     Unversioned API Routes (api/routes/)                     Versioned API Routes (api/v2/)
   ┌─────────────────────────────────────┐                   ┌──────────────────────────────┐
   │ GET  /health                        │                   │ POST /api/v2/predict         │
   │ GET  /locations                     │                   └──────────────┬───────────────┘
   │ POST /predict (Baseline Champion)   │                                  │
   └──────────────────┬──────────────────┘                                  ▼
                      │                                        Pydantic Validation Layer
                      ▼                                        (schemas/prediction_v2.py)
         Model Service (Baseline)                                           │
         (services/model_service.py)                                        ▼
                      │                                    Feature Engineering Service
                      ▼                                    (services/feature_service.py)
         Artifact: house_price.pkl                                          │
         (11 features, 81 locations)                         ┌──────────────┴──────────────┐
                                                             ▼                             ▼
                                                     Geospatial Service             City Grouping
                                                     (geo_service.py)               & Layout Encoding
                                                     (Haversine Metros)                    │
                                                             └──────────────┬──────────────┘
                                                                            │
                                                                            ▼
                                                               Model Service (V2 Candidate)
                                                               (services/model_service_v2.py)
                                                                            │
                                                                            ▼
                                                               Artifact: house_price_v2.pkl
                                                               (16 features, continuous coords)
```

---

## 2. Pre-Existing Contracts (Protected Baseline)

The existing production baseline contracts were strictly preserved without modification:

* **Endpoint:** `POST /predict`
* **Request Contract (`PredictionRequest`):**
  * Numerical: `area_sqft`, `bhk`, `bathroom`, `balcony`, `floor_num`, `total_floors`
  * Categorical: `location`, `Furnishing`, `Transaction`, `facing`, `Ownership`
* **Response Contract (`PredictionResponse`):**
  * `predicted_price` (INR float), `predicted_price_lakhs` (float), `currency: "INR"`, `status: "success"`
* **Locations Registry:** `GET /locations` (Returns 81 verified municipal markets from `locations.json`).
* **Health Check:** `GET /health` (Extended backward-compatibly with `v2_model_loaded`).

---

## 3. V2 API Design

The Valuation Engine V2 is exposed under a dedicated, versioned API prefix:

* **HTTP Method:** `POST`
* **Path:** `/api/v2/predict`
* **Content-Type:** `application/json`
* **Core Philosophy:** **Client sends raw property and location inputs; the backend deterministically engineers all 16 ML features.** The client is never responsible for distance calculations, geometric ratios, or categorical frequency encodings.

---

## 4. Request Schema (`PredictionRequestV2`)

```json
{
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
```

### Field Specifications & Validation Bounds:

| Field Name | Type | Required / Default | Bounds / Domain | Description |
| :--- | :---: | :---: | :---: | :--- |
| `area_sqft` | `float` | **Required** | `> 0`, `≤ 50000` | Property carpet/super-built-up area in sqft. |
| `bhk` | `int` | **Required** | `1 ≤ bhk ≤ 20` | Number of bedrooms. |
| `latitude` | `float` | **Required** | `6.0 ≤ lat ≤ 38.0` | Decimal latitude within India's bounding box. |
| `longitude` | `float` | **Required** | `68.0 ≤ lon ≤ 98.0` | Decimal longitude within India's bounding box. |
| `city` | `str` | Optional (`"other"`) | Text string | Municipality / City name for group mapping. |
| `posted_by` | `str` | Optional (`"Owner"`) | `Owner`, `Dealer`, `Builder` | Listing channel poster entity. |
| `rera` | `int` | Optional (`1`) | `0` or `1` | RERA regulatory approval status. |
| `under_construction` | `int` | Optional (`0`) | `0` or `1` | Property construction status. |
| `ready_to_move` | `int` | Optional (`1`) | `0` or `1` | Immediate possession availability. |
| `resale` | `int` | Optional (`1`) | `0` or `1` | Resale vs primary developer sale. |
| `is_rk` | `int` | Optional (`0`) | `0` or `1` | 1 for Room-Kitchen studio, 0 for BHK. |

---

## 5. Response Schema (`PredictionResponseV2`)

```json
{
  "status": "success",
  "predicted_price": 9236394.38,
  "predicted_price_lakhs": 92.36,
  "currency": "INR",
  "model_version": "2.0.0",
  "model_name": "Valuation Engine V2 (HistGradientBoosting)",
  "engineered_features": {
    "area_per_bhk": 483.871,
    "dist_nearest_metro_km": 0.0,
    "dist_mumbai_km": 834.55,
    "dist_delhi_km": 1741.62,
    "dist_bangalore_km": 0.0,
    "city_grouped": "bangalore"
  }
}
```

---

## 6. Feature Engineering Flow

The backend transforms raw inputs into the exact 16-feature vector expected by the Scikit-Learn `ColumnTransformer`:

1. **Validation:** Pydantic verifies physical dimensions and coordinate boundaries within India.
2. **Geospatial Distances:** Great-circle distances are computed to all 6 Tier-1 Indian metro cores.
3. **Nearest Metro Proxy:** Finds $\min(\text{dist}_{\text{mumbai}}, \text{dist}_{\text{delhi}}, \dots, \text{dist}_{\text{kolkata}})$.
4. **Spatial Density Proxy:** Computes $\text{area\_per\_bhk} = \frac{\text{area\_sqft}}{\text{bhk} + 0.1}$.
5. **Categorical Normalization:** Cleans casing, resolves city aliases, and maps unknown towns to `"other"`.
6. **Inference Execution:** Passes single-row DataFrame to the cached `house_price_v2.pkl` pipeline.

---

## 7. Geospatial Calculations (`geo_service.py`)

* **Great-Circle Distance Formula:** Implemented using the exact spherical Haversine formulation used during Phase 3 model training:
  $$d = 2 R \arcsin \left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$
  where $R = 6371.0 \text{ km}$.
* **Metro Anchor Coordinates:**
  * Mumbai: $(18.9220^\circ\text{N}, 72.8347^\circ\text{E})$
  * Delhi-NCR: $(28.6304^\circ\text{N}, 77.2177^\circ\text{E})$
  * Bangalore: $(12.9716^\circ\text{N}, 77.5946^\circ\text{E})$
  * Hyderabad: $(17.3850^\circ\text{N}, 78.4867^\circ\text{E})$
  * Chennai: $(13.0827^\circ\text{N}, 80.2707^\circ\text{E})$
  * Kolkata: $(22.5726^\circ\text{N}, 88.3639^\circ\text{E})$

---

## 8. City Grouping Logic

* **Recognized Municipal Categories (40):** 39 top Indian municipal hubs (`bangalore`, `mumbai`, `gurgaon`, `chennai`, `kolkata`, `jaipur`, `pune` $\rightarrow$ `other`, etc.) + `other`.
* **Alias Resolution:**
  * `"Bengaluru"` $\rightarrow$ `"bangalore"`
  * `"Bombay"` $\rightarrow$ `"mumbai"`
  * `"Gurugram"` $\rightarrow$ `"gurgaon"`
  * `"Calcutta"` $\rightarrow$ `"kolkata"`
  * `"Madras"` $\rightarrow$ `"chennai"`
  * `"Cochin"` $\rightarrow$ `"kochi"`
* **Fallback Behavior:** Any unlisted town or rare village automatically and deterministically falls back to `"other"` without causing an exception.

---

## 9. Model Loading & Lifecycle

* **Zero-Disk-Reload Policy:** Both `house_price.pkl` and `house_price_v2.pkl` are loaded into memory once during application startup via FastAPI's `lifespan(app)` context manager.
* **Warm In-Memory Inference:** Subsequent prediction requests execute against in-memory model pipelines, eliminating disk I/O overhead.

---

## 10. Error Handling & Status Codes

* **`422 Unprocessable Entity`:** Invalid physical bounds (e.g. area $\le 0$), coordinates outside India (e.g. London lat $51.5^\circ$), or invalid categorical values.
* **`503 Service Unavailable`:** Raised via `ModelNotLoadedError` if an inference endpoint is called before the model artifact is loaded.
* **`500 Internal Server Error`:** Controlled response via `generic_exception_handler` preventing internal stack traces from leaking to clients.

---

## 11. Test Suite Results

Full Pytest suite executed across 41 automated tests:

```text
backend/tests/test_health.py::test_root_endpoint PASSED                  [  2%]
backend/tests/test_health.py::test_health_endpoint PASSED                [  4%]
backend/tests/test_locations.py::test_get_locations_success PASSED       [  7%]
backend/tests/test_locations.py::test_known_cities_in_locations PASSED   [  9%]
backend/tests/test_prediction.py::test_predict_valid_property PASSED     [ 12%]
backend/tests/test_prediction.py::test_predict_with_default_optional_fields PASSED [ 14%]
backend/tests/test_prediction.py::test_predict_missing_required_area PASSED [ 17%]
backend/tests/test_prediction.py::test_predict_missing_required_location PASSED [ 19%]
backend/tests/test_prediction.py::test_predict_invalid_negative_area PASSED [ 21%]
backend/tests/test_prediction.py::test_predict_invalid_zero_bhk PASSED   [ 24%]
backend/tests/test_prediction.py::test_predict_floor_exceeds_total_floors PASSED [ 26%]
backend/tests/test_prediction.py::test_predict_unseen_categorical_handling PASSED [ 29%]
backend/tests/test_v2_features.py::test_haversine_distance_accuracy PASSED [ 31%]
backend/tests/test_v2_features.py::test_coordinate_validation PASSED     [ 34%]
backend/tests/test_v2_features.py::test_calculate_metro_distances PASSED [ 36%]
backend/tests/test_v2_features.py::test_city_group_normalization PASSED  [ 39%]
backend/tests/test_v2_features.py::test_construct_v2_features PASSED     [ 41%]
backend/tests/test_v2_features.py::test_feature_service_to_dataframe PASSED [ 43%]
backend/tests/test_v2_features.py::test_feature_construction_invalid_coords_raises PASSED [ 46%]
backend/tests/test_v2_prediction.py::test_v2_predict_golden_bangalore_sample PASSED [ 48%]
backend/tests/test_v2_prediction.py::test_v2_predict_golden_mumbai_luxury_sample PASSED [ 51%]
backend/tests/test_v2_prediction.py::test_v2_predict_with_default_optional_fields PASSED [ 53%]
backend/tests/test_v2_prediction.py::test_v2_predict_rk_studio_layout PASSED [ 56%]
backend/tests/test_v2_prediction.py::test_v2_predict_unobserved_municipality PASSED [ 58%]
backend/tests/test_v2_prediction.py::test_v2_predict_missing_latitude_422 PASSED [ 60%]
backend/tests/test_v2_prediction.py::test_v2_predict_out_of_bounds_latitude_422 PASSED [ 63%]
backend/tests/test_v2_prediction.py::test_v2_predict_out_of_bounds_longitude_422 PASSED [ 65%]
backend/tests/test_v2_prediction.py::test_v2_predict_negative_area_422 PASSED [ 68%]
backend/tests/test_v2_prediction.py::test_health_reports_both_models_loaded PASSED [ 70%]
backend/tests/test_v2_prediction.py::test_root_lists_v2_endpoint PASSED  [ 73%]
backend/tests/test_v2_schemas.py::test_valid_v2_prediction_request PASSED [ 75%]
backend/tests/test_v2_schemas.py::test_v2_prediction_request_defaults PASSED [ 78%]
backend/tests/test_v2_schemas.py::test_v2_prediction_request_missing_required_latitude PASSED [ 80%]
backend/tests/test_v2_schemas.py::test_v2_prediction_request_missing_required_area PASSED [ 82%]
backend/tests/test_v2_schemas.py::test_v2_prediction_request_invalid_area_bounds PASSED [ 85%]
backend/tests/test_v2_schemas.py::test_v2_prediction_request_invalid_bhk_bounds PASSED [ 87%]
backend/tests/test_v2_schemas.py::test_v2_prediction_request_latitude_bounds PASSED [ 90%]
backend/tests/test_v2_schemas.py::test_v2_prediction_request_longitude_bounds PASSED [ 92%]
backend/tests/test_v2_schemas.py::test_v2_prediction_request_posted_by_normalization PASSED [ 95%]
backend/tests/test_v2_schemas.py::test_v2_prediction_request_binary_flags PASSED [ 97%]
backend/tests/test_v2_schemas.py::test_v2_prediction_response_schema PASSED [100%]

======================== 41 passed in 1.24s ========================
```

---

## 12. Golden Test Cases & Performance Benchmarking

### Golden Test Cases:
* **Bangalore Central Standard Apartment:**
  * Inputs: `1500 sqft, 3 BHK, Lat: 12.9716, Lon: 77.5946, Owner, RERA=1, Resale=1`
  * V2 Output: **₹92.36 Lakhs ($₹9,236,394.38 \text{ INR}$)**
  * Status: **PASS**
* **Mumbai South Luxury Flat:**
  * Inputs: `2200 sqft, 4 BHK, Lat: 18.9220, Lon: 72.8347, Builder, RERA=1, Resale=0`
  * V2 Output: **₹1,050.59 Lakhs ($₹105,058,952.11 \text{ INR}$)**
  * Status: **PASS**

### Latency Benchmark (100 sequential requests):
* **Mean Latency:** **14.07 ms**
* **Minimum Latency:** **10.80 ms**
* **Maximum Latency:** **44.52 ms**
* **Cold Startup Time:** $\approx 480 \text{ ms}$ (total startup for both models + locations).

---

## 13. Backward Compatibility Verification

* `POST /predict` remains completely untouched and operational, executing `house_price.pkl`.
* `GET /locations` continues returning all 81 baseline locations.
* `GET /health` returns `{status: "ok", model_loaded: true, v2_model_loaded: true, locations_loaded: true, version: "1.0.0"}`.
* Frontend bundle compilation (`npm run build`) completed cleanly with 0 TypeScript/Vite errors.

---

## 14. Files Changed & Added in Phase 4

### Created Files:
* [`backend/app/services/geo_service.py`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/app/services/geo_service.py) — Haversine distances, metro coordinates, and city grouping.
* [`backend/app/services/feature_service.py`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/app/services/feature_service.py) — 16-feature vector constructor.
* [`backend/app/services/model_service_v2.py`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/app/services/model_service_v2.py) — V2 model lifecycle and inference executor.
* [`backend/app/schemas/prediction_v2.py`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/app/schemas/prediction_v2.py) — Pydantic request and response schemas for V2.
* [`backend/app/api/routes/prediction_v2.py`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/app/api/routes/prediction_v2.py) — Versioned route handler for `POST /api/v2/predict`.
* [`backend/tests/test_v2_schemas.py`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/tests/test_v2_schemas.py) — Schema validation test suite (11 tests).
* [`backend/tests/test_v2_features.py`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/tests/test_v2_features.py) — Feature engineering & distance test suite (7 tests).
* [`backend/tests/test_v2_prediction.py`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/tests/test_v2_prediction.py) — V2 API integration test suite (11 tests).

### Modified Files:
* [`backend/app/core/config.py`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/app/core/config.py) — Added `MODEL_V2_PATH` and `V2_VERSION`.
* [`backend/app/schemas/prediction.py`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/app/schemas/prediction.py) — Added `v2_model_loaded` to `HealthResponse`.
* [`backend/app/api/routes/health.py`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/app/api/routes/health.py) — Integrated `v2_model_loaded` check into health handler.
* [`backend/app/api/__init__.py`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/app/api/__init__.py) — Mounted `prediction_v2_router` under prefix `/api/v2`.
* [`backend/app/main.py`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/app/main.py) — Integrated V2 model loading into `lifespan` and updated root metadata.
* [`backend/tests/conftest.py`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/tests/conftest.py) — Initialized `model_service_v2` in session fixtures.

---

## 15. Known Limitations

1. **Frontend Integration Pending (Phase 5):** The React frontend currently continues to use `/predict` and has not yet been modified to send coordinates or call `/api/v2/predict`.
2. **Reverse Geocoding:** The current backend accepts explicit `latitude` and `longitude`. Reverse geocoding from free-text addresses or interactive pin-dropping will be handled in subsequent frontend/geospatial expansion phases.

---

## 16. Next Phase Prerequisites (Phase 5)

* [x] Versioned API endpoint `/api/v2/predict` live, documented, and passing all tests.
* [x] In-memory caching established with sub-15ms inference latency.
* [x] Deterministic geospatial feature engineering verified against Phase 3 training math.
* [x] Protected baseline fully preserved without regression.

---

## Final Decision

# **PHASE 4 GATE: PASS**
