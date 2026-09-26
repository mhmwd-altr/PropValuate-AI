# PropValuate AI — Pre-Phase 4 Readiness & Integrity Report

**Project:** PropValuate AI — India Real-Estate Intelligence Platform  
**Stage:** Pre-Phase 4 Readiness & Integrity Verification  
**Date:** September 2026  
**Status:** READY FOR PHASE 4  
**Author / Agent:** PropValuate AI Implementation Agent  

---

## 1. Repository Status
* **Current Git Branch:** `main`
* **Latest Commit Hash:** `25fc707` (`phase3: develop and evaluate Valuation Engine V2`)
* **Working Tree:** Clean (0 uncommitted changes, synchronized with `origin/main`).
* **Protected Paths:** `backend/app/`, `backend/models/house_price.pkl`, `backend/models/locations.json`, `frontend/src/` remain completely intact.

---

## 2. Phase Status Matrix

| Phase Identifier | Scope & Core Objective | Phase Gate Status |
| :--- | :--- | :---: |
| **Phase 0** | Environment, Repository & Recovery | **PASS** |
| **Phase 1** | Product, Architecture & Data Audit | **PASS** |
| **Baseline Run** | Environment Tools Setup & E2E Valuation Verification | **PASS** |
| **Phase 2** | Data Discovery & India Coverage (48k raw listings) | **PASS** |
| **Phase 2.5** | Dataset Selection & Evidence Review (Modular Data Strategy) | **PASS** |
| **Phase 3** | Valuation Engine V2 (Multi-Model Benchmark & Candidate) | **PASS** |

---

## 3. Artifacts Verified

All project artifacts across Phases 0 through 3 were cryptographically verified on disk:

| Artifact File Path | File Size | Status / Description |
| :--- | :---: | :--- |
| [`backend/models/house_price.pkl`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/models/house_price.pkl) | 454.52 KB | **Champion Baseline Model** (Unmodified, 81 cities) |
| [`backend/models/house_price_v2.pkl`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/models/house_price_v2.pkl) | 467.85 KB | **Valuation Engine V2 Candidate** (256 municipalities) |
| [`backend/models/locations.json`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/models/locations.json) | 1.36 KB | **Approved 81 Location Registry** (Unmodified) |
| [`models/registry/model_v2_metadata.json`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/models/registry/model_v2_metadata.json) | 1.59 KB | Machine-readable metadata & hyperparameters for V2 |
| [`models/registry/multi_model_comparison.json`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/models/registry/multi_model_comparison.json) | 1.87 KB | 6-model cross-validation benchmark matrix |
| [`reports/phase3_model_comparison.md`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/reports/phase3_model_comparison.md) | 13.07 KB | 22-section official Phase 3 comparison report |
| [`reports/phase3_error_analysis.md`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/reports/phase3_error_analysis.md) | 6.41 KB | Granular error analysis across price, area, & cities |
| [`notebooks/phase3_valuation_engine_v2.ipynb`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/notebooks/phase3_valuation_engine_v2.ipynb) | 14.50 KB | Fully executed and reproducible Jupyter notebook |

---

## 4. Baseline Integrity
* **Model Object:** `sklearn.pipeline.Pipeline`
* **Regressor:** `HistGradientBoostingRegressor`
* **File Size:** 454.52 KB
* **SHA256 Checksum:** `3538c355847fada24c6d4b6bd052c2362293bbd24ea43938cae83949ed170a33`
* **Status:** **PERFECTLY PRESERVED**. Zero modifications or overwrites have occurred.

---

## 5. V2 Candidate Integrity
* **Model Object:** `sklearn.pipeline.Pipeline` wrapping `TransformedTargetRegressor` (log1p transform) on `HistGradientBoostingRegressor`
* **File Size:** 467.85 KB
* **SHA256 Checksum:** `780a10c8aefa47390945389f7e685b1aae1ed8ed5d8d3d0749fb3468c50cf3c3`
* **Status:** **LOADS AND OPERATES CLEANLY**. Verified via `joblib.load()`.

---

## 6. V2 Feature Contract Specification

Extracted directly from the serialized `ColumnTransformer` inside `house_price_v2.pkl`:

### Numerical Features (14):
1. `area_sqft`: Surface area in square feet ($[100, 15000]$).
2. `bhk`: Number of bedrooms ($[1, 10]$).
3. `is_rk`: Binary flag for Room-Kitchen studio layout ($0$ or $1$).
4. `rera`: Binary flag for RERA regulatory registration ($0$ or $1$).
5. `under_construction`: Construction lifecycle state ($0$ or $1$).
6. `ready_to_move`: Immediate possession availability ($0$ or $1$).
7. `resale`: Transaction type ($1 = \text{Resale}, 0 = \text{Primary Developer Sale}$).
8. `latitude`: Geographic latitude in decimal degrees ($[6.0, 38.0]^\circ\text{N}$).
9. `longitude`: Geographic longitude in decimal degrees ($[68.0, 98.0]^\circ\text{E}$).
10. `area_per_bhk`: Interaction ratio ($\text{area\_sqft} / (\text{bhk} + 0.1)$).
11. `dist_nearest_metro_km`: Great-circle distance to closest tier-1 metro core in km.
12. `dist_mumbai_km`: Distance to Mumbai commercial core in km.
13. `dist_delhi_km`: Distance to Delhi-NCR Connaught Place in km.
14. `dist_bangalore_km`: Distance to Bangalore MG Road in km.

### Categorical Features (2):
15. `posted_by`: Transaction agent entity (`Owner`, `Dealer`, `Builder`).
16. `city_grouped`: Top 50 Indian municipalities (unseen/rare municipalities mapped to `'other'`).

---

## 7. Direct Inference Verification (V2 Candidate)

Direct evaluation of `house_price_v2.pkl` on sample records:

* **Test Sample 1 (Bangalore Central Apartment):**
  * Input: `1500 sqft, 3 BHK, Bangalore Central (12.9716 N, 77.5946 E), RERA=1, Resale=1, Owner`
  * Output: **₹93.12 Lakhs ($₹9,312,339.74 \text{ INR}$)**
  * Latency: **42.14 ms**
  * Validity: Output is non-NaN, strictly positive, and economically coherent.
* **Test Sample 2 (Mumbai South Luxury Flat):**
  * Input: `2200 sqft, 4 BHK, Mumbai South (18.9220 N, 72.8347 E), RERA=1, Resale=0, Builder`
  * Output: **₹673.16 Lakhs ($₹67,315,892.50 \text{ INR}$)**
  * Validity: Output reflects premium coastal metropolitan pricing.

---

## 8. Baseline vs V2 Comparative Snapshot

| Metric / Dimension | Protected Champion Baseline (`house_price.pkl`) | Valuation Engine V2 Candidate (`house_price_v2.pkl`) |
| :--- | :---: | :---: |
| **Training Scope** | 81 Cities (MagicBricks 151k rows) | **256 Municipalities** (National Challenge 29k rows) |
| **Mean Absolute Error (MAE)** | ₹28.08 Lakhs ($₹2,808,000 \text{ INR}$) | **₹23.61 Lakhs ($₹2,361,000 \text{ INR}$)** *(15.9% Error Reduction)* |
| **Median Relative Error (MdAPE)** | $\sim 19.5\%$ | **$16.28\%$** |
| **5-Fold Cross-Validation $R^2$** | **$0.7668 \pm 0.0102$** | **$0.7515 \pm 0.0745$** |
| **Test $R^2$** | **0.7570** | **0.7324** |
| **Geospatial Coordinates** | None (Discrete city strings only) | **Continuous Latitude / Longitude** |
| **Regulatory Tracking** | None | **RERA Approved ($+61.0\%$ Premium)** |
| **Channel Pricing** | None | **Owner vs Dealer vs Builder** |

---

## 9. Important Limitations & Operational Constraints

1. **V2 is NOT Yet Production-Connected:** The current live FastAPI `/predict` endpoint continues to execute the 11-feature contract via `house_price.pkl`. V2 requires coordinate ingestion and distance-to-metro calculators before exposure.
2. **V2 Does Not Dominate Every Single Metric:** While V2 achieves a significantly lower Mean Absolute Error (₹23.61L vs ₹28.08L) across 256 cities, the baseline achieved a slightly higher CV $R^2$ ($0.7668$ vs $0.7515$) on its restricted 81-city corpus.
3. **Geographic Generalization Bounds on Unseen Municipalities:**
   * GroupKFold evaluation on completely withheld cities yielded:
     $$\text{Unseen City } R^2 = 0.5437 \pm 0.2183, \quad \text{MAE} = ₹38.10 \text{ Lakhs}$$
   * The model retains reasonable predictive power on unfamiliar towns, but errors are higher than on observed municipal hubs.
4. **Production API Remains Protected:** No production endpoints or schemas will be broken. Phase 4 will design clean, versioned API architectures (e.g. `/api/v2/predict`).

---

## 10. Existing System Regression Check
* **Pytest Test Suite:** `12 passed in 0.61s` ([pytest backend/tests](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/pytest.ini)).
* **Live Health Check:** `GET /health` $\rightarrow$ `{"status": "ok", "model_loaded": true, "locations_loaded": true, "version": "1.0.0"}`.
* **Live Baseline Prediction:** `POST /predict` $\rightarrow$ `{"predicted_price": 39085954.13, "predicted_price_lakhs": 390.86, "status": "success"}`.
* **Frontend Bundle Compilation:** `tsc -b && vite build` passed cleanly with 0 errors in 4.58s.

---

## 11. Phase 4 Prerequisites
* [x] Champion baseline preserved and verified.
* [x] Candidate V2 model artifact serialized and operational.
* [x] V2 feature schema and coordinate inputs clearly defined.
* [x] All test suites passing without regressions.
* [x] Clean Git working tree.

---

## 12. Final Decision

**READY FOR PHASE 4**
