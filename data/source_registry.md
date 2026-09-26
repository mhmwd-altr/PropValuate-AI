# PropValuate AI — Source Registry (Data Lineage & Licensing)

This registry provides the official, evidence-based data provenance, legal licensing, download methods, checksums, and architectural status for all candidate and baseline datasets investigated during **Phase 2 — Data Discovery & India Coverage**.

---

## 1. Master Source Registry Table

| Dataset Identifier | Source / Platform | Direct URL | Publisher / Author | Version / Date | License / Terms | Download Method | Status | Intended Use |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **india_housing_challenge** | MachineHack / GitHub | [srikanth2102/Predict-the-house-prices-in-India](https://raw.githubusercontent.com/srikanth2102/Predict-the-house-prices-in-India/master/train.csv) | MachineHack / Srikanth | 2020 / Competition Dataset | Open / Public Domain (CC0 Equivalent) | Direct HTTP GET / Verified SHA256 | **ACCEPT FOR MODELING** | Nationwide multi-city property valuation foundation with coordinate-level spatial features and RERA regulatory tracking. |
| **bengaluru_house_prices** | Kaggle / GitHub | [codebasics/py/DataScience/BangloreHomePrices](https://raw.githubusercontent.com/codebasics/py/master/DataScience/BangloreHomePrices/model/bengaluru_house_prices.csv) | Amitabh Sharma / Codebasics | 2019 / v1.0 | CC0: Public Domain | Direct HTTP GET / Verified SHA256 | **ACCEPT FOR FUTURE ANALYSIS** | Bengaluru micro-market spatial resolution and hyper-local sub-market pricing benchmark. |
| **india_house_rent** | Kaggle / GitHub | [Athulyachandran/House-Rent-Dataset-Analysis](https://raw.githubusercontent.com/Athulyachandran/House-Rent-Dataset-Analysis/main/House_Rent_Dataset.csv) | Athulya Chandran (Magicbricks & 99acres aggregation) | July 2022 | CC0: Public Domain | Direct HTTP GET / Verified SHA256 | **ACCEPT FOR FUTURE ANALYSIS** | Future Rental Yield Engine & rental-to-capital valuation ratio modeling across 6 Tier-1 Metros. |
| **delhi_magicbricks_flats** | MagicBricks / GitHub | [Gaurav-223344/Delhi-House-Price-Prediction](https://raw.githubusercontent.com/Gaurav-223344/Delhi-House-Price-Prediction/master/MagicBricks.csv) | Gaurav / Magicbricks Scraped Corpus | 2020 / v1.0 | Open Data / Educational Research | Direct HTTP GET / Verified SHA256 | **ACCEPT FOR FUTURE ANALYSIS** | Capital micro-market feature exploration (e.g., parking, builder floor vs apartment structural types). |
| **baseline_magicbricks_81cities** | Kaggle (Baseline Reference) | Archival Kaggle Mirror (`notebooks/data/house_prices.csv`) | Kaggle / Community Scraped Corpus | 2022 Baseline | Public Domain (Educational/Demo) | Serialized in Baseline Artifacts | **PROTECTED BASELINE REFERENCE** | Serves as the protected 81-city reference standard and ground truth for baseline regression safety. |

---

## 2. Detailed Dataset Lineage & Integrity Verification

### Dataset 1: `india_housing_challenge_train.csv`
* **Local Path:** `data/raw/india_housing_challenge_train.csv`
* **File Format:** CSV (Comma-Separated Values, UTF-8)
* **File Size:** 2,480,917 bytes (2.42 MB)
* **SHA256 Checksum:** `e75eb823fae83713f01b17b38eb146747b0a3ce57f49557451296bf11516e881`
* **Row Count:** 29,451 listings
* **Column Count:** 12 features
* **Licensing / Legal Terms:** Open competition benchmark published under standard open community terms. No proprietary restrictions or non-commercial constraints identified. Attribution requested to original challenge organizers.
* **Geographic Scope:** India-wide (256 extracted cities across 20+ states and union territories, 63 matches with 81-city baseline).
* **Critical Finding:** Source file contains swapped column headers between `LONGITUDE` and `LATITUDE`. Swapped coordinates corrected in audit pipeline.

---

### Dataset 2: `bengaluru_house_prices.csv`
* **Local Path:** `data/raw/bengaluru_house_prices.csv`
* **File Format:** CSV (Comma-Separated Values, UTF-8)
* **File Size:** 924,703 bytes (903.03 KB)
* **SHA256 Checksum:** `0bfbe1b4f4c89932130eec9a795be2e008d519ffeaefd01991ad3d7e5d8b76c6`
* **Row Count:** 13,320 listings
* **Column Count:** 9 features
* **Licensing / Legal Terms:** CC0: Public Domain dedication. Free for commercial, non-commercial, modification, and redistribution use without mandatory attribution.
* **Geographic Scope:** City-specific (Bengaluru Metropolitan Region, 1,295 unique localities).
* **Quality Limitations:** High missingness in `society` (41.3%), text-formatted ranges in `total_sqft`.

---

### Dataset 3: `india_house_rent.csv`
* **Local Path:** `data/raw/india_house_rent.csv`
* **File Format:** CSV (Comma-Separated Values, UTF-8)
* **File Size:** 566,957 bytes (553.67 KB)
* **SHA256 Checksum:** `0ec58a699c824c16f272a8785340ceb8ffcff054cfa2281a7dbcbda2e67df16d`
* **Row Count:** 4,746 listings
* **Column Count:** 12 features
* **Licensing / Legal Terms:** CC0: Public Domain. Open access property rental listing dataset.
* **Geographic Scope:** 6 Major Tier-1 Metros (Mumbai, Bangalore, Chennai, Hyderabad, Delhi, Kolkata).
* **Temporal Scope:** April 13, 2022 to July 11, 2022 (Q2 2022 market snapshot).
* **Target Metric:** Monthly Rent in INR (`Rent`).

---

### Dataset 4: `delhi_magicbricks_flats.csv`
* **Local Path:** `data/raw/delhi_magicbricks_flats.csv`
* **File Format:** CSV (Comma-Separated Values, UTF-8)
* **File Size:** 157,576 bytes (153.88 KB)
* **SHA256 Checksum:** `301ba16198f2b84742a0fe5c866f772ba8beabda5e1c0eef1d48c8bcf62b7810`
* **Row Count:** 1,259 listings
* **Column Count:** 11 features
* **Licensing / Legal Terms:** Open Dataset (Magicbricks Delhi listings). Research and development use permitted.
* **Geographic Scope:** New Delhi & NCR micro-markets (365 distinct localities).
* **Leakage Warning:** Column `Per_Sqft` contains direct algebraic leakage (`Price / Area`) and is strictly forbidden from direct model input vectors.

---

## 3. Preservation & Security Notice
* All raw CSV files located in `data/raw/` are **read-only source materials**. No in-place modification or silent deletion is permitted.
* All data pipelines must load raw files via deterministic read paths and export cleaned artifacts into `data/processed/`.
