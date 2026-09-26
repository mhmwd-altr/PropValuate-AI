# PropValuate AI — Phase 5 Frontend Product Shell: Inspection & Readiness Audit

**Project:** PropValuate AI — India Real-Estate Intelligence Platform  
**Stage:** Phase 5 — Step 1: Frontend Inspection & Readiness Audit  
**Status:** READY FOR PHASE 5 IMPLEMENTATION  
**Date:** September 2026  
**Author / Agent:** PropValuate AI Implementation Agent  

---

## 1. Executive Summary

This audit represents the comprehensive inspection of the **React + TypeScript + Vite** frontend repository to evaluate its architecture, user flow, component hierarchy, and readiness for transition from the baseline `POST /predict` API to the verified **Valuation Engine V2 API (`POST /api/v2/predict`)**.

* **Git State:** Synchronized with `origin/main` at commit `e7fc745` (`phase4: complete final inference parity and architecture verification`). Working tree is clean.
* **Current Frontend Status:** The frontend is fully functional, cleanly structured with Tailwind CSS, Lucide icons, and React Router v6, but currently connects strictly to the unversioned baseline endpoint (`POST /predict`).
* **V2 Transition Path:** The frontend requires targeted updates to support raw V2 inputs (`latitude`, `longitude`, `city`, `posted_by`, `rera`, `ready_to_move`, `under_construction`, `resale`, `is_rk`) and display V2 metadata (`model_version: "2.0.0"`, derived distance proxies).
* **Dependencies:** **Zero new npm packages required.** The existing dependencies (`react`, `react-dom`, `react-router-dom`, `lucide-react`, `clsx`, `tailwind-merge`, `tailwindcss`) provide all necessary tools.

---

## 2. Git & Repository Integrity

* **Branch:** `main`
* **Latest Verified Commit:** [`e7fc745`](https://github.com/mhmwd-altr/PropValuate-AI/commit/e7fc745)
* **Remote Synchronization:** Fully up to date with `https://github.com/mhmwd-altr/PropValuate-AI.git`.
* **Working Tree:** Clean (0 untracked or modified application files).

---

## 3. Frontend Architecture Inventory

The frontend codebase is organized into modular directories under [`frontend/src/`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/frontend/src):

```text
frontend/src/
├── api/
│   └── predictionClient.ts          # Singleton HTTP API client for backend communication
├── components/
│   ├── Header.tsx                   # Top navigation bar with branding & engine status
│   ├── Footer.tsx                   # Technical methodology, metadata & copyright footer
│   ├── InputField.tsx               # Reusable accessible numeric/text input with icons & error states
│   ├── SelectField.tsx              # Reusable styled select dropdown with options & error states
│   └── PredictionForm.tsx           # Multi-section interactive valuation form & client-side validation
├── data/
│   └── locations.json               # Bundled fallback dataset of 81 verified municipal locations
├── pages/
│   ├── HomePage.tsx                 # Landing container with hero banner, feature badges, & PredictionForm
│   ├── ResultPage.tsx               # High-impact valuation result page, animated price, & property specs
│   └── NotFoundPage.tsx             # 404 Route fallback
├── types/
│   └── prediction.ts                # TypeScript interfaces for request, response, errors, & navigation state
├── utils/
│   ├── formatters.ts                # INR currency (Intl), Lakhs/Crore denomination, and location formatters
│   └── useAnimatedNumber.ts         # Smooth RAF-based numeric easing hook for dominant price display
├── App.tsx                          # App shell, routing layout (BrowserRouter), & global container
├── index.css                        # Tailwind directives, keyframe animations, & reduced-motion accessibility
└── main.tsx                         # React 18 DOM mount entry point
```

### Key Technical Stack:
* **Framework:** React 18.3.1
* **Build System:** Vite 6.0.1 + `@vitejs/plugin-react` 4.3.4
* **Language:** TypeScript 5.6.3 (Strict mode enabled)
* **Routing:** `react-router-dom` 6.28.0
* **Styling:** TailwindCSS 3.4.16 + PostCSS 8.4.49 + Autoprefixer 10.4.20
* **Icons:** `lucide-react` 0.468.0
* **Utilities:** `clsx` 2.1.1, `tailwind-merge` 2.5.5

---

## 4. Existing User Flow Trace

```text
[User Lands on /]
       │
       ▼
[HomePage.tsx] ──> Fetches /locations via predictionClient.getLocations()
       │
       ▼
[PredictionForm.tsx]
  ├── User inputs: area_sqft, bhk, bathroom, balcony, floor_num, total_floors, location, Furnishing, Transaction, facing, Ownership
  ├── Real-time client validation checks bounds & logical constraints (e.g. floor ≤ total_floors)
  └── User clicks "Estimate Property Value"
       │
       ▼
[predictionClient.predict(formData)]
  └── Sends HTTP POST to http://localhost:8000/predict (Baseline Model)
       │
       ▼
[FastAPI Backend /predict]
  └── Evaluates house_price.pkl and returns { predicted_price, predicted_price_lakhs, currency, status }
       │
       ▼
[navigate('/result', { state: { inputs, result, timestamp } })]
       │
       ▼
[ResultPage.tsx]
  ├── Animates valuation price via useAnimatedNumber hook (e.g. ₹1.25 Cr)
  ├── Displays breakdown: rate per sqft, property specifications grid, and methodology note
  └── Provides CTAs: "Back to Edit Specifications" or "Valuate Another Property"
```

---

## 5. Contract Comparison: Current Frontend vs Verified V2 API

| Dimension | Current Baseline Form (`PredictionForm.tsx`) | Verified V2 API (`POST /api/v2/predict`) | Compatibility Verdict | Action Required in Phase 5 |
| :--- | :--- | :--- | :---: | :--- |
| **Endpoint** | `POST /predict` | `POST /api/v2/predict` | **GAP** | Point client to `/api/v2/predict`. |
| **`area_sqft`** | Collected (`InputField.tsx`, `1 - 50,000`) | Required (`gt=0, le=50000`) | **MATCH** | Retain input. |
| **`bhk`** | Collected (`InputField.tsx`, `1 - 20`) | Required (`ge=1, le=20`) | **MATCH** | Retain input. |
| **`latitude`** | **Not Collected** | **Required** (`6.0 ≤ lat ≤ 38.0`) | **GAP** | Supply via city coordinate registry / coordinate input. |
| **`longitude`** | **Not Collected** | **Required** (`68.0 ≤ lon ≤ 98.0`) | **GAP** | Supply via city coordinate registry / coordinate input. |
| **`city`** | Collected as `location` slug (e.g. `"bangalore"`) | Optional (`city: str`, defaults to `"other"`) | **MATCH / REFINEMENT** | Pass selected city string to `city`. |
| **`posted_by`** | **Not Collected** | Optional (`"Owner"`, `"Dealer"`, `"Builder"`) | **GAP** | Add segmented selector (Default: `"Owner"`). |
| **`rera`** | **Not Collected** | Optional (`1` = Approved, `0` = Non-RERA) | **GAP** | Add RERA status toggle (Default: `1`). |
| **`ready_to_move`** | **Not Collected** | Optional (`1` = Yes, `0` = No) | **GAP** | Add possession status selector (Default: `1`). |
| **`under_construction`**| **Not Collected** | Optional (`1` = Yes, `0` = No) | **GAP** | Synchronize with possession status. |
| **`resale`** | Partial (Inside `Transaction` dropdown) | Optional (`1` = Resale, `0` = New Sale) | **GAP** | Map transaction type or provide clean toggle. |
| **`is_rk`** | **Not Collected** | Optional (`1` = RK Studio, `0` = BHK) | **GAP** | Add property layout switch (BHK vs 1 RK). |
| **`bathroom` / `balcony`**| Collected for baseline model | Ignored by V2 (Not in V2 contract) | **BASELINE ONLY** | Can retain as secondary specs or streamline for V2. |
| **`floor_num` / `total_floors`**| Collected for baseline model | Ignored by V2 | **BASELINE ONLY** | Retain or organize in structural specs section. |
| **`Furnishing` / `facing` / `Ownership`**| Collected for baseline model | Ignored by V2 | **BASELINE ONLY** | Retain as optional metadata or secondary specs. |
| **Response Metadata**| Displays price & rate/sqft | Returns `model_version`, `model_name`, `engineered_features` | **GAP** | Display V2 Engine badge and derived metro distance proxy. |

---

## 6. Location & Geospatial UX Audit

1. **Current Mechanism:**
   * Fetches location strings from `GET /locations` on mount.
   * Renders a searchable/standard HTML `<select>` with 81 sorted city strings (e.g. `"bangalore"`, `"mumbai"`, `"pune"`, `"gurgaon"`).
   * Falls back to bundled `locations.json` if backend is temporarily unreachable.
2. **Geospatial Gap for V2:**
   * V2 requires decimal `latitude` and `longitude`.
   * **Solution for Phase 5:** Create a comprehensive **City Coordinates Registry** mapping each Indian municipality to its verified centroid coordinates (e.g., Bangalore $\rightarrow$ `(12.9716, 77.5946)`, Mumbai South $\rightarrow$ `(18.9220, 72.8347)`, Delhi-NCR $\rightarrow$ `(28.6304, 77.2177)`).
   * When user selects a city, coordinates are automatically populated, with an optional toggle for advanced manual coordinate adjustments.
3. **Feature Engineering Guardrail:**
   * **The frontend must NEVER calculate distances or feature ratios.**
   * The backend's `feature_service.py` calculates `dist_mumbai_km`, `dist_nearest_metro_km`, and `area_per_bhk`.

---

## 7. UI & Product Quality Audit

* **Visual Hierarchy:** Excellent. Uses clean typography (Inter), curated slate/brand color palettes, and modern card styling.
* **Form Usability:** Structured in logical numbered sections with clear labels, placeholders, and units (`sq ft`, `BHK`).
* **Currency Representation:** Uses `Intl.NumberFormat('en-IN')` and compact Lakhs/Crore badges (`₹1.25 Cr`, `₹92.36 Lakhs`).
* **Result Presentation:** Dominant hero card with animated counter (`useAnimatedNumber`), followed by property specification grid and methodology disclaimer.
* **Validation Feedback:** Instant real-time error messages under each invalid field, with an alert banner on top for API/server errors.
* **Mobile Responsiveness:** Fully responsive grid (`grid-cols-1 md:grid-cols-3 lg:grid-cols-4`) with touch-friendly tap targets and collapsible layout.
* **Accessibility:** Semantic HTML, ARIA attributes, explicit labels, and `prefers-reduced-motion` keyframe overrides.

---

## 8. Preserved Behaviors (Protection Rules)

The following existing capabilities must be protected during Phase 5:
1. **Zero Fake/Hardcoded AI:** Every valuation must come directly from the live FastAPI endpoint.
2. **Graceful Direct Navigation Fallback:** If `/result` is accessed directly without prediction state, render the graceful "No Valuation Available" redirect card.
3. **Form State Retention on Back Navigation:** Clicking "Back to Edit Specifications" must preserve previously entered form values.
4. **Copy-to-Clipboard Summary:** Must generate formatted summary text.
5. **No Breaking Changes to Baseline Backend:** Backend `/predict` and `/locations` endpoints remain untouched.

---

## 9. Phase 5 Implementation Blueprint

### A. MUST CHANGE (Core V2 Integration)
1. [`frontend/src/types/prediction.ts`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/frontend/src/types/prediction.ts):
   * Add `PredictionRequestV2` interface (`area_sqft`, `bhk`, `latitude`, `longitude`, `city`, `posted_by`, `rera`, `under_construction`, `ready_to_move`, `resale`, `is_rk`).
   * Add `PredictionResponseV2` interface with `model_version`, `model_name`, and `engineered_features`.
2. [`frontend/src/api/predictionClient.ts`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/frontend/src/api/predictionClient.ts):
   * Add `predictV2(request: PredictionRequestV2): Promise<PredictionResponseV2>` targeting `${this.baseUrl}/api/v2/predict`.
   * Retain `predict(request: PredictionRequest)` for baseline compatibility.
3. `frontend/src/data/cityCoordinates.ts`:
   * Create city coordinate directory with accurate latitude/longitude pairs for top 81+ Indian municipal hubs.
4. [`frontend/src/components/PredictionForm.tsx`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/frontend/src/components/PredictionForm.tsx):
   * Update form state to include V2 fields.
   * Connect city selection to automatic coordinate resolution.
   * Add selectors for Transaction Party (`Owner`/`Dealer`/`Builder`), RERA approval, Possession status, and Property Layout (`BHK`/`RK`).
   * Call `predictionClient.predictV2(formData)`.
5. [`frontend/src/pages/ResultPage.tsx`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/frontend/src/pages/ResultPage.tsx):
   * Render V2 Valuation Engine badge (`v2.0.0`).
   * Display engineered spatial distance chips (e.g. `Distance to Metro Core`, `Area per room`).

### B. SHOULD CHANGE (UX & Polish)
1. [`frontend/src/pages/HomePage.tsx`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/frontend/src/pages/HomePage.tsx):
   * Update hero badge and description to reflect Valuation Engine V2 (Continuous Geospatial AI across India).
2. Segmented Pill Buttons:
   * Replace basic select dropdowns for binary options (`RERA: Yes/No`, `Ready to Move / Under Construction`, `Resale / New Sale`) with sleek segmented button groups.

### C. OPTIONAL (Future Phases)
* Interactive Leaflet / Mapbox map pin picker for custom lat/lon coordinates.
* Multi-language interface (Hindi / regional languages).

---

## 10. Proposed Measurable Acceptance Criteria

1. **Build & Type Safety:** `npm run build` compiles with 0 TypeScript and Vite errors.
2. **V2 API Handshake:** Submitting the form initiates a `POST` request to `/api/v2/predict` and receives HTTP 200.
3. **Golden Case Verification (Bangalore):** Submitting `1500 sqft, 3 BHK, Bangalore` produces $\approx ₹92.36 \text{ Lakhs}$ valuation on `/result`.
4. **Golden Case Verification (Mumbai):** Submitting `2200 sqft, 4 BHK, Mumbai South, Builder` produces luxury valuation on `/result`.
5. **Geospatial Coordinates:** Selecting any city automatically supplies valid latitude/longitude within India bounds.
6. **Error Resilience:** Backend disconnection produces user-friendly error banners without crashing the application.
7. **Form State Continuity:** Clicking "Back to Edit Specifications" restores all entered parameters.
8. **Responsive Layout:** Form and result cards render without horizontal overflow across mobile (375px), tablet (768px), and desktop (1280px).

---

## 11. Answers to the 15 Explicit Questions

1. **What exact frontend files currently control valuation?**
   * [`frontend/src/components/PredictionForm.tsx`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/frontend/src/components/PredictionForm.tsx) (Input collection, state, and submission)
   * [`frontend/src/api/predictionClient.ts`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/frontend/src/api/predictionClient.ts) (API fetch calls)
   * [`frontend/src/pages/HomePage.tsx`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/frontend/src/pages/HomePage.tsx) (Page container)
   * [`frontend/src/pages/ResultPage.tsx`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/frontend/src/pages/ResultPage.tsx) (Valuation display)
   * [`frontend/src/types/prediction.ts`](file:///c:/Users/mhmwd/OneDrive/Desktop/PropValuate-AI-main/frontend/src/types/prediction.ts) (Type definitions)

2. **What exact backend endpoint does the frontend currently call?**
   * `POST /predict` (line 59 in `predictionClient.ts`).

3. **What exact payload does it currently send?**
   * `{ area_sqft, bhk, bathroom, balcony, floor_num, total_floors, location, Furnishing, Transaction, facing, Ownership }`.

4. **What V2 fields are missing from the current UI?**
   * `latitude`, `longitude`, `city`, `posted_by`, `rera`, `under_construction`, `ready_to_move`, `resale`, `is_rk`.

5. **Where should each missing field come from?**
   * `latitude` & `longitude`: Auto-resolved from city coordinate registry or refined by user.
   * `city`: Selected from municipal city selector.
   * `posted_by`: Segmented button (`Owner` / `Dealer` / `Builder`).
   * `rera`: Toggle button (`RERA Approved` Yes/No).
   * `ready_to_move` / `under_construction`: Toggle button (`Ready to Move` vs `Under Construction`).
   * `resale`: Toggle button (`Resale` vs `New Property`).
   * `is_rk`: Layout switch (`BHK` vs `1 RK Studio`).

6. **How should latitude/longitude be supplied to the V2 API?**
   * Pre-mapped municipal centroid coordinates matched to the selected city, with an optional coordinate refinement toggle.

7. **Is `/locations` currently integrated into the frontend?**
   * Yes, fetched in `PredictionForm.tsx` on mount via `predictionClient.getLocations()`.

8. **Does the current location representation match the backend's accepted city values?**
   * Yes. The backend's `geo_service.py` normalizes all standard Indian city slugs (e.g. `"bangalore"`, `"mumbai"`, `"gurgaon"`).

9. **Does the frontend currently calculate any model features that should instead remain backend-owned?**
   * No. Distance to metros and density ratios are strictly computed by the backend `feature_service.py`.

10. **What is the smallest safe set of changes required to make the frontend V2-compatible?**
    * Add V2 interfaces in `prediction.ts`, add `predictV2()` in `predictionClient.ts`, add city coordinates lookup, update `PredictionForm.tsx` to send V2 payload, and update `ResultPage.tsx` to display V2 response.

11. **What changes are purely UX and should not affect model behavior?**
    * Button segmenting, icons, animation transitions, layout organization, copy text, and badge styling.

12. **Are any new npm dependencies actually necessary?**
    * **No new dependencies are required.** The existing React, Tailwind, and Lucide libraries are completely sufficient.

13. **What existing frontend behavior must be protected?**
    * Client-side validation, error handling banners, back navigation state persistence, currency formatting, and responsive design.

14. **What exact files do you propose modifying in the implementation phase?**
    * `frontend/src/types/prediction.ts`
    * `frontend/src/api/predictionClient.ts`
    * `frontend/src/components/PredictionForm.tsx`
    * `frontend/src/pages/HomePage.tsx`
    * `frontend/src/pages/ResultPage.tsx`
    * `frontend/src/data/cityCoordinates.ts` (new dataset file)

15. **What tests/evidence will prove Phase 5 is actually working?**
    * Clean Vite production build (`npm run build`).
    * Full end-to-end browser valuation run connecting to `/api/v2/predict` and rendering ₹92.36L for Bangalore and ₹1,050.59L for Mumbai.
    * Validation error tests.

---

## 12. Final Gate Decision

# **READY FOR PHASE 5 IMPLEMENTATION**
