# PropValuate AI — Phase 4 Final Inference Parity Check Report

**Project:** PropValuate AI — India Real-Estate Intelligence Platform  
**Stage:** Phase 4 Final — Inference & Architectural Parity Verification  
**Date:** September 2026  
**Final Status:** PASS — PHASE 4 FULLY VERIFIED  
**Author / Agent:** PropValuate AI Implementation Agent  

---

## 1. Executive Summary

This parity verification rigorously tested that the live **FastAPI Version 2 Endpoint (`POST /api/v2/predict`)** produces exact mathematical parity with **Direct Scikit-Learn Inference on `backend/models/house_price_v2.pkl`** across identical raw inputs. Furthermore, category mappings and geospatial constants were verified against the Phase 3 training codebase to ensure zero drift.

---

## 2. Direct V2 vs API V2 Parity Benchmark

The identical raw property inputs were fed into both:
* **Method A (Direct V2):** In-memory evaluation via Scikit-Learn `Pipeline.predict()` on DataFrame.
* **Method B (API V2):** Live HTTP POST request to `/api/v2/predict` processed through FastAPI, Pydantic validation, and the Feature Engineering Service.

| Property Benchmark Sample | Raw Property Inputs | Direct V2 Prediction | API V2 Prediction | Absolute Difference (INR) | Parity Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Bangalore Central Apartment** | `1500 sqft, 3 BHK, 12.9716°N, 77.5946°E, City: bangalore, Owner, RERA=1, Resale=1` | **₹92.36 Lakhs** ($₹9,236,394.38$) | **₹92.36 Lakhs** ($₹9,236,394.38$) | **₹0.0014 INR** | **EXACT MATCH (PASS)** |
| **Mumbai South Luxury Flat** | `2200 sqft, 4 BHK, 18.9220°N, 72.8347°E, City: mumbai, Builder, RERA=1, Resale=0` | **₹1,050.59 Lakhs** ($₹105,058,952.11$) | **₹1,050.59 Lakhs** ($₹105,058,952.11$) | **₹0.0005 INR** | **EXACT MATCH (PASS)** |
| **Delhi-NCR Gurgaon Builder Floor** | `1800 sqft, 3 BHK, 28.4595°N, 77.0266°E, City: gurgaon, Dealer, RERA=1, UnderConst=1, Resale=0` | **₹125.60 Lakhs** ($₹12,559,575.34$) | **₹125.60 Lakhs** ($₹12,559,575.34$) | **₹0.0049 INR** | **EXACT MATCH (PASS)** |
| **Unobserved Tier-2 Municipality (Tirupati)** | `1400 sqft, 3 BHK, 13.6288°N, 79.4192°E, City: tirupati, Owner, RERA=1, Resale=1` | **₹53.74 Lakhs** ($₹5,374,014.57$) | **₹53.74 Lakhs** ($₹5,374,014.57$) | **₹0.0039 INR** | **EXACT MATCH (PASS)** |

* **Max Floating-Point Variance:** $< ₹0.005 \text{ INR}$ (due solely to float rounding during JSON formatting).
* **Parity Result:** **100% Deterministic Equivalence**.

---

## 3. City Category & Encodings Parity

The categories extracted directly from the fitted `OneHotEncoder` transformer inside `house_price_v2.pkl` were compared against the backend's `TOP_CITIES_V2` set in `backend/app/services/geo_service.py`:

* **Trained `posted_by` Categories (3):** `['Builder', 'Dealer', 'Owner']` $\rightarrow$ **Exact Match**.
* **Trained `city_grouped` Categories (40):**
  `['agra', 'aurangabad', 'bangalore', 'bhopal', 'bhubaneswar', 'chennai', 'coimbatore', 'dehradun', 'durgapur', 'faridabad', 'gandhinagar', 'ghaziabad', 'goa', 'gurgaon', 'guwahati', 'gwalior', 'jaipur', 'jamnagar', 'jamshedpur', 'kochi', 'kolkata', 'lalitpur', 'lucknow', 'maharashtra', 'mohali', 'mumbai', 'nagpur', 'other', 'palghar', 'patna', 'raigad', 'rajkot', 'ranchi', 'secunderabad', 'siliguri', 'sonipat', 'surat', 'thrissur', 'vijayawada', 'visakhapatnam']`
* **Discrepancies (Trained $-$ Backend):** **0 (None)**
* **Discrepancies (Backend $-$ Trained):** **0 (None)**
* **Fallback Behavior:** All unobserved municipalities correctly and deterministically map to `'other'`.

---

## 4. Geospatial Calculation & Formula Parity

The geospatial feature extraction in `backend/app/services/geo_service.py` was checked against the Phase 3 training implementation (`scripts/train_valuation_v2.py`):

* **Earth Radius Parameter:** $R = 6371.0 \text{ km}$ (Exact Match).
* **Metro Anchor Coordinates:**
  * Mumbai: $(18.9220^\circ\text{N}, 72.8347^\circ\text{E})$ — Match: **True**
  * Delhi-NCR: $(28.6304^\circ\text{N}, 77.2177^\circ\text{E})$ — Match: **True**
  * Bangalore: $(12.9716^\circ\text{N}, 77.5946^\circ\text{E})$ — Match: **True**
  * Hyderabad: $(17.3850^\circ\text{N}, 78.4867^\circ\text{E})$ — Match: **True**
  * Chennai: $(13.0827^\circ\text{N}, 80.2707^\circ\text{E})$ — Match: **True**
  * Kolkata: $(22.5726^\circ\text{N}, 88.3639^\circ\text{E})$ — Match: **True**
* **Distance Accuracy Test (Bangalore $\rightarrow$ Mumbai):**
  * Training Calculation: $834.54974132 \text{ km}$
  * Inference Calculation: $834.54974132 \text{ km}$
  * Absolute Difference: **$0.000000000000 \text{ km}$**

---

## 5. Regression & Integration Verification

* **Pytest Suite:** `41 passed in 1.04s` ([pytest backend/tests](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/pytest.ini)).
* **`GET /health`:** Returns `{status: "ok", model_loaded: true, v2_model_loaded: true, locations_loaded: true, version: "1.0.0"}`.
* **`POST /predict` (Baseline Protected):** Returns ₹124.66 Lakhs ($₹12,465,981.21$) for Bangalore baseline sample.
* **`POST /api/v2/predict` (V2 Candidate):** Returns ₹92.36 Lakhs ($₹9,236,394.38$) with derived spatial metadata.
* **Frontend Compilation:** `tsc -b && vite build` succeeded in 4.93s with 0 errors.

---

## 6. Final Status

# **PASS — PHASE 4 FULLY VERIFIED**
