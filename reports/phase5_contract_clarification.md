# PropValuate AI — Phase 5 Final Contract Clarification Check

**Project:** PropValuate AI — India Real-Estate Intelligence Platform  
**Stage:** Phase 5 — Pre-Implementation Final Contract Clarification  
**Status:** CONTRACT FULLY CLARIFIED — READY FOR IMPLEMENTATION  
**Date:** September 2026  
**Author / Agent:** PropValuate AI Implementation Agent  

---

## 1. Existing `/locations` Contract Evidence

### Backend Implementation:
* **Route File:** [`backend/app/api/routes/locations.py`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/app/api/routes/locations.py#L7-L21)
* **Service File:** [`backend/app/services/location_service.py`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/app/services/location_service.py#L10-L58)
* **Underlying Artifact:** [`backend/models/locations.json`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/models/locations.json)
* **Response Schema (`LocationsResponse`):**
  ```python
  class LocationsResponse(BaseModel):
      total_locations: int = Field(..., description="Total number of verified locations", examples=[81])
      locations: List[str] = Field(..., description="List of verified city/location strings")
  ```
* **Exact Total Locations Returned:** **81**
* **Real Sample Content:**
  ```json
  {
    "total_locations": 81,
    "locations": [
      "agra", "ahmadnagar", "ahmedabad", "allahabad", "aurangabad",
      "badlapur", "bangalore", "belgaum", "bhiwadi", "bhiwandi",
      "bhopal", "bhubaneswar", "chandigarh", "chennai", "coimbatore", ...
    ]
  }
  ```
* **Coordinate Presence:** **None**. The locations array contains discrete 1D strings only; it contains no latitude or longitude fields.
* **Canonical City Values:** Yes, each string is a lowercase slug corresponding to a recognized Indian municipality.

### Frontend Consumption Evidence:
* **API Client Request:** [`frontend/src/api/predictionClient.ts:24-52`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/frontend/src/api/predictionClient.ts#L24-L52)
  * Requests `GET ${this.baseUrl}/locations` with Accept `application/json`.
  * Fallback to [`frontend/src/data/locations.json`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/frontend/src/data/locations.json) if fetch fails.
* **TypeScript Interface:** [`frontend/src/types/prediction.ts:22-25`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/frontend/src/types/prediction.ts#L22-L25)
  * `export interface LocationsResponse { total_locations: number; locations: string[]; }`
* **UI Consumer:** [`frontend/src/components/PredictionForm.tsx:88-115`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/frontend/src/components/PredictionForm.tsx#L88-L115)
  * Loads on mount, sorts alphabetically, and populates the `<SelectField name="location" />` options.

---

## 2. Location $\rightarrow$ Coordinate Strategy Evidence

### A. Existing Canonical Coordinate Source
* **Repository Search Result:** **NO comprehensive canonical 81-city coordinate mapping file currently exists in `backend/` or `frontend/`.**
* **Existing Partial Coordinates:**
  * [`backend/app/services/geo_service.py`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/app/services/geo_service.py#L12-L19) contains anchor coordinates for the 6 Tier-1 Metros (`mumbai`, `delhi`, `bangalore`, `hyderabad`, `chennai`, `kolkata`).
  * The raw dataset `india_housing_challenge_train.csv` contains raw individual listing coordinates, but no aggregated city centroid lookup table.

### B. V2 Model Requirement
* **Why Coordinates are Mandatory:**
  * Valuation Engine V2 (`house_price_v2.pkl`) requires continuous numeric features `latitude` and `longitude` to compute great-circle Haversine distances to Tier-1 metros (`dist_nearest_metro_km`, `dist_mumbai_km`, `dist_delhi_km`, `dist_bangalore_km`).
  * City string alone is insufficient for spatial distance calculation. Both `city` and `(latitude, longitude)` must be supplied in the request.

### C. Unknown / Unmapped City Behavior
* If a user submits coordinates for an unmapped town or unlisted municipality:
  * The Pydantic validator verifies that `latitude` $\in [6.0, 38.0]$ and `longitude` $\in [68.0, 98.0]$.
  * The backend `geo_service.normalize_city_group(city)` maps the city string to `'other'`.
  * The model successfully predicts price using spatial coordinates and `'other'` category.
  * If coordinates are missing, Pydantic raises HTTP `422 Unprocessable Entity`.

### D. Coordinate Precision
* The training pipeline and model use standard 4-decimal place float precision (e.g. `12.9716, 77.5946`), providing $\sim 11\text{ meters}$ ground resolution.

---

## 3. V2 Request Field Semantics (Phase 4 Schema Evidence)

Extracted directly from [`backend/app/schemas/prediction_v2.py`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/app/schemas/prediction_v2.py#L4-L88) and [`backend/app/services/feature_service.py`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/backend/app/services/feature_service.py#L38-L98):

| Field Name | Type | Required? | Allowed / Validated Values | Backend Validation Mechanism |
| :--- | :---: | :---: | :---: | :--- |
| **`area_sqft`** | `float` | **Yes** | `> 0` and `≤ 50000` | Pydantic `gt=0, le=50000` |
| **`bhk`** | `int` | **Yes** | `1` to `20` | Pydantic `ge=1, le=20` |
| **`latitude`** | `float` | **Yes** | `6.0` to `38.0` | Pydantic `ge=6.0, le=38.0` & `is_valid_india_coordinate()` |
| **`longitude`** | `float` | **Yes** | `68.0` to `98.0` | Pydantic `ge=68.0, le=98.0` & `is_valid_india_coordinate()` |
| **`city`** | `str` | Optional (default: `"other"`) | Any string slug/name | Normalized by `normalize_city_group()` $\rightarrow$ Top 39 + `'other'` |
| **`posted_by`** | `str` | Optional (default: `"Owner"`) | `'Owner'`, `'Dealer'`, `'Builder'` | Pydantic `field_validator` (case-insensitive title normalization) |
| **`rera`** | `int` | Optional (default: `1`) | `0` or `1` | Pydantic `ge=0, le=1` |
| **`under_construction`** | `int` | Optional (default: `0`) | `0` or `1` | Pydantic `ge=0, le=1` |
| **`ready_to_move`** | `int` | Optional (default: `1`) | `0` or `1` | Pydantic `ge=0, le=1` |
| **`resale`** | `int` | Optional (default: `1`) | `0` or `1` | Pydantic `ge=0, le=1` |
| **`is_rk`** | `int` | Optional (default: `0`) | `0` or `1` | Pydantic `ge=0, le=1` |

---

## 4. Mutual Exclusivity & Boolean Semantics Evidence

1. **`under_construction` vs `ready_to_move`:**
   * **Backend Evidence:** In `PredictionRequestV2`, both fields have individual `ge=0, le=1` constraints. There is **no cross-field validator in Pydantic enforcing mutual exclusivity**.
   * **Domain & Dataset Reality:** In Indian residential real estate, a unit is either ready to move (`ready_to_move=1, under_construction=0`) or under construction (`ready_to_move=0, under_construction=1`).
   * **Frontend Recommendation:** A single segmented 2-state toggle (`"Ready to Move"` vs `"Under Construction"`) sets both fields correctly without ambiguous states.
2. **`rera`:** Strictly binary (`1` = RERA Approved, `0` = Non-RERA).
3. **`resale`:** Strictly binary (`1` = Secondary Resale, `0` = Primary Developer Sale).
4. **`is_rk`:** Strictly binary (`1` = Room-Kitchen Studio, `0` = Standard BHK).

---

## 5. `posted_by` Contract Evidence

* **Pydantic Validation:**
  ```python
  @field_validator("posted_by")
  @classmethod
  def validate_posted_by(cls, v: str) -> str:
      cleaned = str(v).strip().title()
      if cleaned not in {"Owner", "Dealer", "Builder"}:
          raise ValueError("Invalid posted_by. Must be one of: 'Owner', 'Dealer', 'Builder'.")
      return cleaned
  ```
* **Trained Model Categories:** Extracted from `house_price_v2.pkl` `OneHotEncoder`:
  $$\text{Categories} = [\text{'Builder'}, \text{'Dealer'}, \text{'Owner'}]$$
* **Parity Status:** **100% Match**.

---

## 6. Current Baseline Frontend Payload Inspection

Extracted from [`frontend/src/components/PredictionForm.tsx:28-40`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/frontend/src/components/PredictionForm.tsx#L28-L40):

```json
{
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
```

### Mapping to V2 Contract:

| Current Field | Source in UI | Mapping to V2 | Notes |
| :--- | :--- | :--- | :--- |
| `area_sqft` | `<InputField name="area_sqft" />` | `area_sqft` | Direct 1:1 match |
| `bhk` | `<InputField name="bhk" />` | `bhk` | Direct 1:1 match |
| `location` | `<SelectField name="location" />` | `city` + (`latitude`, `longitude`) | City name maps to `city`; coordinates resolved via lookup |
| `Transaction` | `<SelectField name="Transaction" />` | `resale` | `'Resale'` $\rightarrow 1$, `'New Property'` $\rightarrow 0$ |
| `bathroom`, `balcony` | `<InputField />` | Ignored by V2 | Kept in baseline only |
| `floor_num`, `total_floors` | `<InputField />` | Ignored by V2 | Kept in baseline only |
| `Furnishing`, `facing`, `Ownership` | `<SelectField />` | Ignored by V2 | Kept in baseline only |
| `posted_by` | *Not in baseline UI* | `posted_by` | New segmented selector (`Owner` / `Dealer` / `Builder`) |
| `rera` | *Not in baseline UI* | `rera` | New toggle (`1` / `0`) |
| `ready_to_move` / `under_construction` | *Not in baseline UI* | `ready_to_move`, `under_construction` | New toggle (`Ready to Move` vs `Under Construction`) |
| `is_rk` | *Not in baseline UI* | `is_rk` | New layout switch (`BHK` vs `1 RK`) |

---

## 7. Recommended Location Architecture

### Decision: **Option B (Canonical City Identity via `/locations` + Client-Side Coordinate Registry)**

**Why Option B is the only safe approach based on repository evidence:**
1. **Protected Baseline Contract:** Backend `/locations` returns `{ total_locations: 81, locations: string[] }`. Modifying its schema to add coordinates would alter a protected baseline contract tested by existing test suites.
2. **Deterministic & Offline-Resilient:** A client-side coordinate registry (`cityCoordinates.ts`) guarantees accurate municipal centroid coordinates for all 81 cities without network latency or additional API roundtrips.
3. **Graceful Customization:** When a user selects a city (e.g. `bangalore`), the frontend populates `city = "bangalore"`, `latitude = 12.9716`, `longitude = 77.5946`. An optional "Customize Coordinates" toggle allows fine-grained manual input for power users.

---

## 8. Remaining Risks & Mitigations

* **Risk 1: Missing coordinate for an unlisted custom city.**  
  * *Mitigation:* The frontend defaults coordinates to India's national center or the nearest metro centroid if a user types a custom town, or prompts the user for coordinates.
* **Risk 2: Breaking existing `/predict` baseline.**  
  * *Mitigation:* `predictionClient.ts` will retain `predict()` targeting `/predict` while adding `predictV2()` targeting `/api/v2/predict`.

---

## 9. Final Decision

### **CONTRACT FULLY CLARIFIED — READY FOR IMPLEMENTATION**
