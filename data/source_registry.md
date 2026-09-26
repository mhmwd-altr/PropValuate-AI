# PropValuate AI — Source Registry (Data Lineage & Licensing)

This registry provides the official, evidence-based data provenance, legal licensing, download methods, checksums, and architectural status for all candidate, baseline, and macroeconomic reference datasets investigated during **Phase 2 & Phase 2.5 — Dataset Selection & Evidence Review**.

---

## 1. Master Source Registry Table

| Dataset Identifier | Source / Platform | Direct URL | Publisher / Author | Version / Date | License / Terms | Download Method | Status | Architectural Role |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`india_housing_challenge_train`** | MachineHack / GitHub | [srikanth2102/Predict-the-house-prices-in-India](https://raw.githubusercontent.com/srikanth2102/Predict-the-house-prices-in-India/master/train.csv) | MachineHack & Analytics India Magazine | 2020 Benchmark | Open Data / Public Benchmark | Direct HTTP GET / Verified SHA256 | **ACCEPTED** | **PRIMARY TRAINING DATA** (Nationwide residential sale price valuation engine). |
| **`india_housing_challenge_test`** | MachineHack / GitHub | [srikanth2102/Predict-the-house-prices-in-India](https://raw.githubusercontent.com/srikanth2102/Predict-the-house-prices-in-India/master/test.csv) | MachineHack & Analytics India Magazine | 2020 Benchmark | Open Data / Public Benchmark | Direct HTTP GET / Verified SHA256 | **ACCEPTED** | **AUXILIARY / OUT-OF-SAMPLE SPATIAL BENCHMARK** (68,720 listings for spatial parsing & unlabelled inference testing). |
| **`bengaluru_house_prices`** | Kaggle / GitHub | [codebasics/py/DataScience/BangloreHomePrices](https://raw.githubusercontent.com/codebasics/py/master/DataScience/BangloreHomePrices/model/bengaluru_house_prices.csv) | Amitabh Sharma / Codebasics | 2019 / v1.0 | CC0: Public Domain | Direct HTTP GET / Verified SHA256 | **ACCEPTED** | **SECONDARY TRAINING DATA / REGIONAL BENCHMARK** (Dedicated Bengaluru hyper-local pricing module). |
| **`india_house_rent`** | Kaggle / GitHub | [Athulyachandran/House-Rent-Dataset-Analysis](https://raw.githubusercontent.com/Athulyachandran/House-Rent-Dataset-Analysis/main/House_Rent_Dataset.csv) | Athulya Chandran (Magicbricks & 99acres aggregation) | July 2022 | CC0: Public Domain | Direct HTTP GET / Verified SHA256 | **ACCEPTED** | **FUTURE MARKET INTELLIGENCE (RENTAL ENGINE)** (Excluded from sale price models; basis for rental yield analysis). |
| **`delhi_magicbricks_flats`** | MagicBricks / GitHub | [Gaurav-223344/Delhi-House-Price-Prediction](https://raw.githubusercontent.com/Gaurav-223344/Delhi-House-Price-Prediction/master/MagicBricks.csv) | Gaurav / Magicbricks Scraped Corpus | 2020 / v1.0 | Open Data / Educational Research | Direct HTTP GET / Verified SHA256 | **ACCEPTED** | **AUXILIARY / MICRO-MARKET BENCHMARK** (Specialized structural typology testing under strict `Per_Sqft` leakage exclusion). |
| **`nhb_residex_hpi`** | National Housing Bank (NHB) | [NHB Publications / Housing Price Indices](https://nhb.org.in/publications/housing-price-indices/) | Government of India / NHB | 2018–2024 (Quarterly) | Official Open Government Publication | API / Quarterly PDF & Table Ingestion | **ACCEPTED (MACRO)** | **AUXILIARY / MACROECONOMIC INFLATION BENCHMARK** (Time-series city price appreciation indexing). |
| **`baseline_magicbricks_81cities`** | Kaggle (Baseline Reference) | Archival Kaggle Mirror (`notebooks/data/house_prices.csv`) | Kaggle / Community Scraped Corpus | 2022 Baseline | Public Domain (Educational/Demo) | Serialized in Baseline Artifacts | **PROTECTED BASELINE** | **HISTORICAL CONTROL & REGRESSION BASELINE** (81-city reference standard for baseline safety). |

---

## 2. Detailed Dataset Lineage & Integrity Verification

### Dataset 1: `india_housing_challenge_train.csv`
* **Local Path:** `data/raw/india_housing_challenge_train.csv`
* **File Format:** CSV (Comma-Separated Values, UTF-8)
* **File Size:** 2,480,917 bytes (2.42 MB)
* **SHA256 Checksum:** `e75eb823fae83713f01b17b38eb146747b0a3ce57f49557451296bf11516e881`
* **Row Count:** 29,451 listings
* **Column Count:** 12 features
* **Licensing / Legal Terms:** Open competition benchmark published under standard open community terms. Free for modeling and evaluation.
* **Geographic Scope:** India-wide (256 extracted cities across 20+ states and union territories, 63 matches with 81-city baseline).
* **Critical Finding:** Source file contains inverted column headers (`LONGITUDE` holds latitudes; `LATITUDE` holds longitudes). Re-mapped in parsing pipelines.

---

### Dataset 2: `india_housing_challenge_test.csv`
* **Local Path:** `data/raw/india_housing_challenge_test.csv`
* **File Format:** CSV (Comma-Separated Values, UTF-8)
* **File Size:** 5,424,547 bytes (5.17 MB)
* **SHA256 Checksum:** `6e11aa5c5f3b794121bf303f84f291e0a29792476d054d7fca7e584f27be1e46`
* **Row Count:** 68,720 listings
* **Column Count:** 11 features (Unlabelled target)
* **Licensing / Legal Terms:** Open competition benchmark.
* **Geographic Scope:** India-wide (Coordinates and addresses across 500+ micro-markets).
* **Architectural Role:** Out-of-sample unlabelled test bench for geospatial feature extractor robustness.

---

### Dataset 3: `bengaluru_house_prices.csv`
* **Local Path:** `data/raw/bengaluru_house_prices.csv`
* **File Format:** CSV (Comma-Separated Values, UTF-8)
* **File Size:** 924,703 bytes (903.03 KB)
* **SHA256 Checksum:** `0bfbe1b4f4c89932130eec9a795be2e008d519ffeaefd01991ad3d7e5d8b76c6`
* **Row Count:** 13,320 listings
* **Column Count:** 9 features
* **Licensing / Legal Terms:** **CC0: Public Domain** dedication. Free for commercial, modification, and redistribution use.
* **Geographic Scope:** City-specific (Bengaluru Metropolitan Region, 1,295 unique localities).
* **Quality Limitations:** High missingness in `society` (41.3%), text-formatted ranges in `total_sqft`.

---

### Dataset 4: `india_house_rent.csv`
* **Local Path:** `data/raw/india_house_rent.csv`
* **File Format:** CSV (Comma-Separated Values, UTF-8)
* **File Size:** 566,957 bytes (553.67 KB)
* **SHA256 Checksum:** `0ec58a699c824c16f272a8785340ceb8ffcff054cfa2281a7dbcbda2e67df16d`
* **Row Count:** 4,746 listings
* **Column Count:** 12 features
* **Licensing / Legal Terms:** **CC0: Public Domain**.
* **Geographic Scope:** 6 Major Tier-1 Metros (Mumbai, Bangalore, Chennai, Hyderabad, Delhi, Kolkata).
* **Temporal Scope:** April 13, 2022 to July 11, 2022 (Q2 2022 market snapshot).
* **Target Metric:** Monthly Rent in INR (`Rent`). Strictly segregated from capital price models.

---

### Dataset 5: `delhi_magicbricks_flats.csv`
* **Local Path:** `data/raw/delhi_magicbricks_flats.csv`
* **File Format:** CSV (Comma-Separated Values, UTF-8)
* **File Size:** 157,576 bytes (153.88 KB)
* **SHA256 Checksum:** `301ba16198f2b84742a0fe5c866f772ba8beabda5e1c0eef1d48c8bcf62b7810`
* **Row Count:** 1,259 listings
* **Column Count:** 11 features
* **Licensing / Legal Terms:** Open Dataset (Magicbricks Delhi listings). Research and development use permitted.
* **Geographic Scope:** New Delhi & NCR micro-markets (365 distinct localities).
* **Leakage Warning:** Column `Per_Sqft` contains direct algebraic leakage ($\text{Price} / \text{Area}$) and is strictly forbidden from direct model input vectors.

---

## 3. Preservation & Security Notice
* All raw CSV files located in `data/raw/` are **read-only source materials**. No in-place modification or silent deletion is permitted.
* All data pipelines must load raw files via deterministic read paths and export cleaned artifacts into `data/processed/`.
