# Phase 1: Product, Architecture & Data Audit Report
**Project:** PropValuate AI — India  
**Target Specification:** PropValuate AI India Master Project Guide V3  
**Status:** Audit Completed  
**Date:** September 2026  
**Auditor:** Primary Engineering Agent  

---

## Executive Summary
This report presents an evidence-based audit of the existing **PropValuate AI** repository against the requirements of the approved **PropValuate AI India Master Project Guide V3**. 

The current system represents a validated, working single-model machine learning web application for estimating residential property prices across 81 Indian cities. The baseline is robust and fully functional, passing all unit tests, builds, and sanity predictions. However, its current monolithic design, single-source Kaggle dataset, static categorical representations, and lack of uncertainty bounds require structured, phase-gated expansion to support the multimodal AI real-estate platform defined in the Master Guide.

---

## 1. Current Architecture Map

### High-Level Topology
The current application consists of three decoupled layers:
1. **Data & ML Training Layer (Offline):** Located in `notebooks/`. Reads raw Kaggle listings (`notebooks/data/house_prices.csv`), performs cleaning and feature engineering, trains a 4-model benchmark, and exports two artifacts into `backend/models/`:
   - `house_price.pkl` (454.5 KB serialized Scikit-Learn pipeline)
   - `locations.json` (1.3 KB JSON file containing 81 supported city strings)
2. **Backend Services Layer (Asynchronous REST API):** Located in `backend/`. An asynchronous FastAPI service wrapping the serialized ML pipeline and locations metadata into three endpoints (`/health`, `/locations`, `/predict`).
3. **Frontend Client Layer (Single-Page Application):** Located in `frontend/`. A React 18 + TypeScript + Vite + Tailwind CSS application providing real-time client validation, dynamic dropdown population, and animated price presentation.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DATA & TRAINING LAYER                           │
│  notebooks/data/house_prices.csv (187,531 raw listings)                │
│                         │                                              │
│                         ▼                                              │
│  notebooks/house_price_model.ipynb (54 cells: EDA, cleaning, 4 models) │
│                         │                                              │
│           ┌─────────────┴─────────────┐                                │
│           ▼                           ▼                                │
│  backend/models/house_price.pkl  backend/models/locations.json         │
└───────────────────┬───────────────────────────┬────────────────────────┘
                    │                           │
┌───────────────────┼───────────────────────────┼────────────────────────┐
│                   ▼                           ▼                        │
│             ModelService               LocationService                 │
│                   │                           │                        │
│                   └─────────────┬─────────────┘                        │
│                                 ▼                                      │
│                        FASTAPI BACKEND SERVICE                         │
│                  Endpoints: /health, /locations, /predict              │
│                                 ▲                                      │
└─────────────────────────────────┼──────────────────────────────────────┘
                                  │ JSON / HTTP
┌─────────────────────────────────┴──────────────────────────────────────┐
│                       REACT + TYPESCRIPT CLIENT                        │
│  HomePage (Input Form) ─── POST /predict ───► ResultPage (Animated UI) │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Frontend Component & Route Map

### 2.1 Route Architecture (`frontend/src/App.tsx`)
The React client uses `react-router-dom` (v6.28.0 with `v7_startTransition` and `v7_relativeSplatPath` enabled):
- **`/` (`HomePage`):** Landing page and primary input interface. Renders hero copy, trust badges, and the interactive `PredictionForm`.
- **`/result` (`ResultPage`):** Valuation reveal interface. Reads valuation results and inputs passed via router state (`location.state`), drives the animated price counter, displays localized denomination chips (`₹ Lakhs` / `₹ Cr`), and shows a breakdown of submitted parameters.
- **`*` (`NotFoundPage`):** 404 fallback page providing navigation back to the valuation tool.

### 2.2 Reusable UI Components (`frontend/src/components/`)
- **`Header.tsx`:** Sticky application navigation header with branding, status pill, and GitHub repository link.
- **`Footer.tsx`:** Standard application footer with copyright, tech stack chips, and dataset attribution.
- **`PredictionForm.tsx`:** Multi-section interactive form containing 11 input controls, client-side validation logic, submit state management, and API dispatch.
- **`InputField.tsx`:** Reusable wrapper for numeric inputs featuring labels, icons, units (e.g. `sq ft`, `BHK`), helper text, and inline validation error messages.
- **`SelectField.tsx`:** Reusable wrapper for dropdown selects featuring custom chevron icons, options mapping, and error display.

### 2.3 Utilities & Custom Hooks (`frontend/src/utils/`)
- **`useAnimatedNumber.ts`:** Custom React animation hook using `requestAnimationFrame` and an ease-out cubic interpolation curve to animate numeric values smoothly over 850ms.
- **`formatters.ts`:**
  - `formatINR(val)`: Formats numbers into standard Indian Rupee notation (`₹1,24,65,981`).
  - `formatIndianDenomination(val)`: Converts raw numbers into localized Crores / Lakhs strings (`1.25 Cr` or `85.50 Lakhs`).
  - `formatLocation(loc)`: Capitalizes hyphenated city names (`new-delhi` $\rightarrow$ `New Delhi`).
  - `formatFloor(floor, total)`: Converts numeric floors into human terms (`Basement`, `Ground Floor`, `Floor 4 of 10`).

---

## 3. Backend Endpoint, Schema & Service Map

### 3.1 REST API Routes (`backend/app/api/routes/`)
| Endpoint | Method | Status Code | Purpose | Request Schema | Response Schema |
| :--- | :---: | :---: | :--- | :--- | :--- |
| `/` | `GET` | `200 OK` | Root service metadata & links | None | Plain JSON dict |
| `/health` | `GET` | `200 OK` | Liveness & model readiness check | None | `HealthResponse` |
| `/locations` | `GET` | `200 OK` | List 81 verified city markets | None | `LocationsResponse` |
| `/predict` | `POST` | `200 OK` | Compute residential property price | `PredictionRequest` | `PredictionResponse` |

### 3.2 Pydantic V2 Schemas (`backend/app/schemas/prediction.py`)
- **`PredictionRequest`:** Validates 11 features. Enforces numeric bounds (`area_sqft > 0, <= 50000`, `bhk: 1..20`, `bathroom: 1..20`, `balcony: 0..20`, `floor_num: -5..200`, `total_floors: 1..200`). Implements a `@model_validator(mode='after')` verifying `floor_num <= total_floors` for standard floors.
- **`PredictionResponse`:** Outputs `predicted_price: float` (INR), `predicted_price_lakhs: float`, `currency: "INR"`, `status: "success"`.
- **`LocationsResponse`:** Outputs `total_locations: int` and `locations: List[str]`.
- **`HealthResponse`:** Outputs `status: "ok"`, `model_loaded: bool`, `locations_loaded: bool`, `version: "1.0.0"`.

### 3.3 Backend Services Layer (`backend/app/services/`)
- **`ModelService` (`model_service.py`):** Thread-safe singleton service. Loads `house_price.pkl` during FastAPI startup lifespan. Exposes `predict(feature_data)` which builds a single-row Pandas DataFrame strictly matching the 11 feature names and executes `pipeline.predict()`, clamping output to `max(0.0, val)`.
- **`LocationService` (`location_service.py`):** Thread-safe singleton service. Loads `locations.json` on startup. Exposes `get_locations()`, `get_total_count()`, and `is_valid_location()`.

### 3.4 Error Handling & Status Codes (`backend/app/utils/errors.py`)
- `ModelNotLoadedError` $\rightarrow$ HTTP 503 Service Unavailable
- `LocationDataNotFoundError` $\rightarrow$ HTTP 500 Internal Server Error
- `PredictionExecutionError` $\rightarrow$ HTTP 500 Internal Server Error
- Unhandled general exceptions $\rightarrow$ HTTP 500 Internal Server Error

---

## 4. Current Machine Learning & Data Contract

### 4.1 Raw Dataset Lineage
- **Origin:** Kaggle Indian Housing Prices Dataset (`house_prices.csv`, ~106 MB).
- **Volume:** 187,531 raw property listings spanning 81 metropolitan regions.
- **Filtering:** Deduplication reduced rows to 167,485 unique records. Domain boundaries ($100 \le \text{area} \le 15,000$ sq ft, $₹2\text{L} \le \text{price} \le ₹30\text{Cr}$, $1 \le \text{BHK} \le 10$, $1 \le \text{Bathrooms} \le 10$) yielded 151,847 clean samples.
- **Train/Test Split:** 80/20 train/test split with `random_state=42` ($N_{\text{train}} = 121,477$, $N_{\text{test}} = 30,370$).

### 4.2 Verified 11-Feature Contract
```python
NUMERICAL_FEATURES = [
    'area_sqft',     # Carpet or Super Area in square feet
    'bhk',           # Bedroom count (integer/float)
    'bathroom',      # Bathroom count
    'balcony',       # Balcony count
    'floor_num',     # Vertical property floor (-1=Basement, 0=Ground, 1+=Standard)
    'total_floors'   # Total stories in the building structure
]

CATEGORICAL_FEATURES = [
    'location',      # Lowercase city name (81 supported cities)
    'Furnishing',    # 'Furnished', 'Semi-Furnished', 'Unfurnished'
    'Transaction',   # 'Resale', 'New Property', 'Other', 'Rent/Lease'
    'facing',        # 'East', 'North', 'North - East', 'West', 'South', etc.
    'Ownership'      # 'Freehold', 'Leasehold', 'Co-operative Society', etc.
]
```

### 4.3 Pipeline Architecture & Model Benchmark
The production model artifact `backend/models/house_price.pkl` is an encapsulated Scikit-Learn `Pipeline`:
1. **Preprocessor:** `ColumnTransformer`:
   - Numerical: `SimpleImputer(strategy='median')` $\rightarrow$ `StandardScaler()`
   - Categorical: `SimpleImputer(strategy='constant', fill_value='Unknown')` $\rightarrow$ `OneHotEncoder(handle_unknown='ignore', sparse_output=False)`
2. **Regressor:** `HistGradientBoostingRegressor(max_iter=150, max_leaf_nodes=31, min_samples_leaf=20, random_state=42)`

| Model Architecture | Test MAE | Test RMSE | Test $R^2$ | 5-Fold CV $R^2$ | Artifact Size |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Linear Regression | ₹42.11 Lakhs | ₹87.57 Lakhs | 0.5891 | $0.5901 \pm 0.0094$ | 7.7 KB |
| Ridge Regression ($\alpha=10$) | ₹42.03 Lakhs | ₹87.55 Lakhs | 0.5893 | $0.5902 \pm 0.0094$ | 6.8 KB |
| **HistGradientBoosting (Selected)** | **₹28.08 Lakhs** | **₹67.38 Lakhs** | **0.7570** | **$0.7668 \pm 0.0102$** | **454.5 KB** |
| Random Forest (40 Trees) | ₹28.40 Lakhs | ₹66.39 Lakhs | 0.7640 | $0.7766 \pm 0.0092$ | 22.1 MB |

---

## 5. End-to-End Valuation Request Trace

Tracing a sample request: **1500 sq ft, 3 BHK, 2 Baths, 2 Balconies, Floor 4 of 10, Bangalore, Semi-Furnished, Resale, East Facing, Freehold**:

```
[1] User enters 11 fields in React Form on HomePage.tsx
     │
     ▼
[2] PredictionForm.tsx executes validateForm()
     - Verifies positive numeric values, range limits, and floor_num <= total_floors
     │
     ▼
[3] predictionClient.predict() sends HTTP POST to http://localhost:8000/predict
     Body: { "area_sqft": 1500.0, "bhk": 3, "location": "bangalore", ... }
     │
     ▼
[4] FastAPI routes request to predict_house_price() in backend/app/api/routes/prediction.py
     - Pydantic V2 deserializes and validates against PredictionRequest schema
     - Executes @model_validator checking floor_num <= total_floors
     │
     ▼
[5] model_service.predict(feature_dict) in backend/app/services/model_service.py
     - Assembles single-row Pandas DataFrame matching exact FEATURE_CONTRACT columns
     - Passes DataFrame into self._pipeline.predict(df_input)
     │
     ▼
[6] Scikit-Learn Pipeline execution
     - ColumnTransformer: Imputes missing values, standard-scales numerics, one-hot encodes categoricals
     - HistGradientBoostingRegressor computes continuous INR prediction: 12,465,981.212555788
     │
     ▼
[7] model_service clamps output: max(0.0, val) and returns float
     │
     ▼
[8] Route handler rounds price, derives predicted_price_lakhs = 124.66, returns HTTP 200 OK
     Response: { "predicted_price": 12465981.21, "predicted_price_lakhs": 124.66, ... }
     │
     ▼
[9] predictionClient parses JSON, returns PredictionResponse to PredictionForm
     │
     ▼
[10] React router navigates: navigate('/result', { state: { inputs, result, timestamp } })
     │
     ▼
[11] ResultPage.tsx mounts:
     - useAnimatedNumber interpolates 0 -> 12,465,981 over 850ms
     - formatIndianDenomination renders "1.25 Cr" badge
     - Computes derived rate: ₹8,311 / sq ft
     - Renders submitted specifications summary grid
```

---

## 6. Keep / Modify / Replace / Add Matrix

| Component / Layer | Action | Classification | Rationale & Evidence |
| :--- | :---: | :---: | :--- |
| `backend/models/house_price.pkl` | **KEEP** | CURRENT / IMPLEMENTED | Validated production baseline artifact. Compact (454.5 KB), fast inference (18.9 ms), test $R^2 = 0.7570$. Serves as benchmark for V2. |
| Backend Core Architecture (`FastAPI`, `lifespan`, `services/`) | **KEEP** | CURRENT / IMPLEMENTED | Clean asynchronous service design, thread-safe singletons, organized route modules. |
| 11-Feature Contract Schema | **KEEP** | CURRENT / IMPLEMENTED | Verified baseline interface for tabular property prediction. |
| Existing 12 Backend Tests (`backend/tests/`) | **KEEP** | CURRENT / IMPLEMENTED | Comprehensive regression test suite. Must continue passing throughout future phases. |
| React 18 + Vite + Tailwind CSS UI Foundation | **KEEP** | CURRENT / IMPLEMENTED | Modern, responsive build system with fast HMR and zero TypeScript errors. |
| `backend/app/core/config.py` | **MODIFY** | RECOMMENDED | Currently inherits from `BaseModel` without reading `.env`. Upgrade to `pydantic-settings` to dynamically support deployment environments. |
| `backend/app/schemas/prediction.py` | **MODIFY** | RECOMMENDED | Add Out-of-Distribution (OOD) flag/warning when input values exceed training percentiles (e.g. area $> 15,000$ sq ft). |
| `frontend/src/pages/ResultPage.tsx` | **MODIFY** | RECOMMENDED | Currently relies entirely on transient router state; page refresh resets to blank fallback. Add URL query parameters or session storage caching. |
| Triple-redundant `locations.json` copies | **REPLACE** | RECOMMENDED | `backend/models/locations.json`, `frontend/src/data/locations.json`, and `frontend/public/locations.json` are identical duplicates. Replace with dynamic backend API caching. |
| Hardcoded Frontend Select Options | **REPLACE** | RECOMMENDED | Options for `Furnishing`, `Transaction`, `facing`, `Ownership` are hardcoded in `PredictionForm.tsx`. Replace with a metadata endpoint (`GET /metadata`). |
| Multi-source Indian Real-Estate Data Foundation | **ADD** | PLANNED | Phase 2 requirement: Acquire and profile additional Indian property datasets beyond the single Kaggle file. |
| Valuation Engine V2 (`confidence_interval`, `SHAP`) | **ADD** | PLANNED | Phase 3 requirement: Add uncertainty estimation and feature attribution waterfall outputs. |
| Versioned API Routing (`/api/v1/...`) | **ADD** | RECOMMENDED | Phase 4 requirement: Prevent breaking changes when adding multimodal endpoints. |
| Modular Frontend Workspaces Shell | **ADD** | PLANNED | Phase 5 requirement: Dedicated workspaces for Valuation, Language AI, Computer Vision, and Geospatial Maps. |
| Multimodal AI Services (Language, Vision, Geospatial) | **ADD** | PLANNED | Phases 6–9 requirements: LLM grounding, image attribute extraction, and coordinate-based location intelligence. |

---

## 7. Technical Debt, Duplicated Logic, Obsolete Code & Risky Coupling

### 7.1 Identified Issues
1. **Triplicated Metadata (`locations.json`):**
   - Exact same 81-city JSON file exists in:
     - `backend/models/locations.json`
     - `frontend/src/data/locations.json`
     - `frontend/public/locations.json`
   - *Risk:* Retraining the model and generating a new location list will desynchronize frontend and backend unless manually updated in three locations.
2. **Static Configuration ignoring `.env`:**
   - `backend/app/core/config.py` uses standard Pydantic `BaseModel` rather than `pydantic-settings` `BaseSettings`.
   - *Risk:* Settings like `CORS_ORIGINS`, `HOST`, and `PORT` defined in `backend/.env.example` are not dynamically read from the environment at runtime.
3. **Hardcoded Categorical Options in React:**
   - `PredictionForm.tsx` hardcodes options for `Furnishing`, `Transaction`, `facing`, and `Ownership`.
   - *Risk:* If backend or ML training introduces or alters category values, frontend and backend will fall out of contract alignment.
4. **Transient Result Page State:**
   - `ResultPage.tsx` expects all data from `location.state`. Refreshing the browser or bookmarking the URL causes a fallback to "No Valuation Available".
5. **No Out-of-Distribution (OOD) Guard:**
   - In training, records with `area_sqft > 15,000` were pruned as extreme outliers. The backend schema permits up to `50,000` sq ft without warning the caller that the prediction is extrapolated.

---

## 8. Missing or Weak Validation / Tests

1. **Frontend Testing Absence:**
   - `frontend/package.json` contains no test runner (no Vitest, Jest, or React Testing Library).
   - Component rendering, form state management, and animated hooks have zero automated test coverage.
2. **Missing OOD & Edge Case Tests:**
   - Existing backend tests cover boundary validation (`bhk=0`, negative area, floor > total_floors), but do not test behavior at domain extremes (e.g. area = 49,999 sq ft).
3. **Missing Model Corruption Recovery Test:**
   - Tests do not verify that `ModelNotLoadedError` returns a clean HTTP 503 if the pickle artifact is unreadable or missing.
4. **Browser Subagent Playwright Environment:**
   - The Antigravity IDE browser subagent cannot currently perform automated UI tests due to a 404 response on the upstream Playwright driver CDN (`playwright-1.57.0-win32_x64.zip`). Live HTTP validation currently serves as the validation mechanism.

---

## 9. Protected Baseline Contracts (Must NOT Be Broken)

The following baseline contracts must remain strictly backward-compatible during all future phases:
1. **HTTP Endpoint Contracts:**
   - `GET /health` $\rightarrow$ `{ "status": "ok", "model_loaded": bool, "locations_loaded": bool, "version": str }`
   - `GET /locations` $\rightarrow$ `{ "total_locations": 81, "locations": [...] }`
   - `POST /predict` $\rightarrow$ Accepts 11-feature JSON; returns `{ "predicted_price": float, "predicted_price_lakhs": float, "currency": "INR", "status": "success" }`
2. **The 11 Input Feature Names & Types:**
   - `area_sqft` (float), `bhk` (int/float), `bathroom` (float), `balcony` (float), `floor_num` (float), `total_floors` (float)
   - `location` (lowercase string), `Furnishing` (string), `Transaction` (string), `facing` (string), `Ownership` (string)
3. **Production Benchmark Model:**
   - `backend/models/house_price.pkl` must be retained as the validated baseline benchmark ($R^2 = 0.7570$, MAE = ₹28.08 Lakhs) against which any future Valuation Engine V2 must be compared.

---

## 10. Recommended Target Architecture for Next Stages

Based on the Master Project Guide V3, the recommended target architecture expands the current system without rewriting it:

```
propvaluate-ai/
├── data/                           # Phase 2: Evidence-based data foundation
│   ├── raw/                        # Immutable raw datasets (gitignored)
│   ├── processed/                  # Cleaned, standardized tabular & spatial data
│   ├── metadata/                   # Data dictionaries, source registry, licenses
│   └── source_registry.md          # Dataset origins, timestamps, row counts
├── notebooks/                      # Exploratory Data Analysis & Modeling
│   ├── house_price_model.ipynb     # Baseline ITI model notebook (PRESERVED)
│   ├── data_audit.ipynb            # Phase 2: Multi-source Indian real-estate audit
│   └── valuation_engine_v2.ipynb   # Phase 3: Spatial, OOD & uncertainty modeling
├── backend/
│   ├── app/
│   │   ├── main.py                 # Application root & lifespan management
│   │   ├── core/config.py          # Dynamic environment configuration
│   │   ├── api/
│   │   │   ├── v1/                 # Versioned API routes
│   │   │   │   ├── valuation.py    # /api/v1/predict (V1 baseline + V2 engine)
│   │   │   │   ├── metadata.py     # /api/v1/metadata (locations, options)
│   │   │   │   ├── assistant.py    # Phase 6: Language AI endpoints
│   │   │   │   ├── vision.py       # Phase 7: Computer Vision endpoints
│   │   │   │   └── geospatial.py   # Phase 8: Spatial & transit endpoints
│   │   │   └── routes/             # Legacy baseline routes (/health, /locations, /predict)
│   │   ├── schemas/                # Modular Pydantic schemas by capability
│   │   └── services/
│   │       ├── model_service.py    # Baseline ML inference service (PRESERVED)
│   │       ├── valuation_v2_service.py # Phase 3: Valuation V2 with intervals & SHAP
│   │       ├── assistant_service.py    # Phase 6: Language AI orchestration
│   │       ├── vision_service.py       # Phase 7: Vision inspection service
│   │       └── geospatial_service.py   # Phase 8: Location intelligence service
│   └── models/
│       ├── house_price.pkl         # Baseline model artifact (PRESERVED)
│       └── locations.json          # Verified location registry
└── frontend/
    └── src/
        ├── features/               # Modular capability workspaces
        │   ├── valuation/          # Existing valuation form & result view
        │   ├── assistant/          # Phase 5 & 6: AI conversational interface
        │   ├── vision/             # Phase 5 & 7: Property image analysis workspace
        │   └── geospatial/         # Phase 5 & 8: Interactive location & price map
        ├── api/                    # Typed API clients for each backend service
        └── components/             # Global design system & layout components
```

---

## 11. Classification Summary
- **CURRENT / IMPLEMENTED:**
  - 11-feature tabular valuation model (`HistGradientBoostingRegressor`).
  - FastAPI asynchronous backend (`/health`, `/locations`, `/predict`).
  - React 18 + TypeScript + Vite + Tailwind CSS frontend with real-time validation and animated price counter.
  - 12 automated backend unit and integration tests.
  - 81 supported Indian urban markets.
- **PLANNED (Per Master Guide V3):**
  - Phase 2: Evidence-based data discovery & geographic expansion across India.
  - Phase 3: Valuation Engine V2 with confidence intervals, OOD detection, and SHAP explainability.
  - Phase 4: Formalized backend foundation with versioned endpoints (`/api/v1/...`).
  - Phase 5: Expanded frontend product shell with multi-workspace navigation.
  - Phases 6–12: Language AI, Computer Vision, Geospatial intelligence, multimodal fusion, accounts, and market trends.
- **RECOMMENDED:**
  - Upgrade `config.py` to `pydantic-settings` to dynamically parse `.env`.
  - Consolidate triplicated `locations.json` into a single canonical source.
  - Expose categorical options (`Furnishing`, etc.) via a metadata endpoint.
  - Add Vitest + React Testing Library to frontend `package.json`.
  - Implement URL query parameter or session caching for valuation results.
- **UNKNOWN / NEEDS RESEARCH:**
  - Licensing, geographic granularity, and download feasibility of candidate Indian real-estate datasets for Phase 2.
  - Hardware feasibility and licensing for local self-hosted Language AI and Vision models (Phases 6–7) on this development machine.
  - Resolution of upstream CDN 404 for Playwright driver to enable automated browser testing in Antigravity IDE.

---

## 12. Phase 1 Gate Review & Deferred Issues Register

### Gate Decision: PASS
- **Audit Completeness:** All 10 required audit dimensions (frontend, backend, ML contract, E2E trace, tests, Keep/Modify/Replace/Add matrix, technical debt, validation gaps, protected contracts, and target architecture) are documented with concrete file-level evidence.
- **Baseline Preserved:** No application code was modified, broken, or refactored.
- **Target Alignment:** The target architecture directly operationalizes the modular, phase-gated specification from the Master Project Guide V3.

### Deferred Issues Register (Tracked for Future Phases)
The following identified improvements are intentionally recorded without immediate code changes:
1. **DEFERRED TO PHASE 3 (Valuation Engine V2):**
   - Out-of-Distribution (OOD) percentile bounds checks and warnings for input extremes.
   - Predictive uncertainty intervals and SHAP feature attribution waterfall analysis.
2. **DEFERRED TO PHASE 4 (Backend Foundation & API Contracts):**
   - Upgrade `backend/app/core/config.py` from `pydantic.BaseModel` to `pydantic_settings.BaseSettings` for dynamic `.env` file ingestion.
   - Implement versioned API routing (`/api/v1/...`).
   - Create a metadata endpoint (`GET /api/v1/metadata`) to serve valid categorical values (`Furnishing`, `Transaction`, `facing`, `Ownership`).
   - Eliminate triplicated copies of `locations.json` across repository directories in favor of a single canonical backend source.
3. **DEFERRED TO PHASE 5 (Frontend Product Shell):**
   - Configure Vitest and React Testing Library in `frontend/package.json` for automated frontend test coverage.
   - Implement URL query parameter or session storage caching on `ResultPage.tsx` to preserve valuation state across page refreshes.
   - Scaffold the modular multi-workspace product shell (Valuation, Assistant, Vision, Geospatial, History).
4. **ENVIRONMENT / TOOLING TRACKING:**
   - Upstream CDN resolution for Playwright browser driver (`playwright-1.57.0-win32_x64.zip`) within the Antigravity IDE subagent environment.

