# PropValuate AI — Data Dictionary

This document provides the standardized data dictionary for all features, variables, and target outputs analyzed during **Phase 2 — Data Discovery & India Coverage**.

---

## 1. National Multi-City Dataset (`india_housing_challenge_train.csv`)

| Field Name | Type | Meaning / Definition | Unit | Example Value | Missingness | Expected Usage | Leakage Risk / Audit Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POSTED_BY` | Categorical (String) | Entity listing the property on the exchange | Category (`Owner`, `Dealer`, `Builder`) | `"Dealer"` | 0.0% (0) | Feature (Predictor) | None. Reflects transaction agent profile at listing time. |
| `UNDER_CONSTRUCTION` | Binary (Integer) | Flag indicating whether the property is currently under construction | Binary (`0` = Ready, `1` = Under Construction) | `0` | 0.0% (0) | Feature (Predictor) | None. Valid baseline property lifecycle state. |
| `RERA` | Binary (Integer) | Real Estate Regulatory Authority approval status | Binary (`0` = Unapproved / Non-RERA, `1` = Approved) | `1` | 0.0% (0) | Feature (Predictor) | None. Regulatory compliance feature that correlates with price premiums. |
| `BHK_NO.` | Numeric (Integer) | Number of bedrooms/hall/kitchen units | Integer count | `3` | 0.0% (0) | Feature (Predictor) | None. Room layout structure. |
| `BHK_OR_RK` | Categorical (String) | Property configuration type | Category (`BHK`, `RK`) | `"BHK"` | 0.0% (0) | Feature (Predictor) | None. Distinguishes studio/room-kitchen vs bedroom apartments. |
| `SQUARE_FT` | Numeric (Float) | Total super built-up / carpet area of the dwelling | Square Feet (sqft) | `1350.0` | 0.0% (0) | Feature (Predictor) | None. Core physical property dimension. Extreme outliers (>50k) exist. |
| `READY_TO_MOVE` | Binary (Integer) | Immediate possession availability | Binary (`0` = No, `1` = Yes) | `1` | 0.0% (0) | Feature (Predictor) | None. Inverse correlation with `UNDER_CONSTRUCTION`. |
| `RESALE` | Binary (Integer) | Secondary market transaction vs primary developer sale | Binary (`0` = Primary Sale, `1` = Resale) | `1` | 0.0% (0) | Feature (Predictor) | None. Directly maps to baseline `Transaction` contract. |
| `ADDRESS` | Categorical (String) | Micro-locality and municipality address string | Text string (`"Locality, City"`) | `"Ksfc Layout,Bangalore"` | 0.0% (0) | Feature (Spatial Parsing) | None. Rich spatial hierarchy for city and locality extraction. |
| `LONGITUDE` *(Raw)* | Numeric (Float) | **Raw Header Inversion:** Actually holds Latitude | Decimal Degrees (North) | `12.9699` | 0.0% (0) | Spatial Feature (Latitude) | **Severe Header Inversion:** Must be reassigned to `latitude` in parsing. |
| `LATITUDE` *(Raw)* | Numeric (Float) | **Raw Header Inversion:** Actually holds Longitude | Decimal Degrees (East) | `77.5979` | 0.0% (0) | Spatial Feature (Longitude) | **Severe Header Inversion:** Must be reassigned to `longitude` in parsing. |
| `TARGET(PRICE_IN_LACS)` | Numeric (Float) | Property sale valuation | Lakhs Indian Rupees (100,000 INR) | `65.0` | 0.0% (0) | **Target Variable ($y$)** | **Target Output.** Convert to standard INR via $\times 100,000$. |

---

## 2. Bengaluru Metro Dataset (`bengaluru_house_prices.csv`)

| Field Name | Type | Meaning / Definition | Unit | Example Value | Missingness | Expected Usage | Leakage Risk / Audit Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `area_type` | Categorical (String) | Area measurement standard | Category (`Super built-up Area`, `Plot Area`, `Built-up Area`) | `"Super built-up Area"` | 0.0% (0) | Feature (Predictor) | None. Explains usable space variance. |
| `availability` | Categorical (String) | Delivery status or possession date | Text / Date category (`Ready To Move`, `19-Dec`) | `"Ready To Move"` | 0.0% (0) | Feature (Predictor) | None. Needs temporal standardization. |
| `location` | Categorical (String) | Micro-locality in Bengaluru | Locality name | `"Whitefield"` | 0.01% (1) | Spatial Feature | None. High granularity (1,295 unique micro-markets). |
| `size` | Categorical (String) | Bedroom count formatted as string | Text string (`2 BHK`, `4 Bedroom`) | `"2 BHK"` | 0.12% (16) | Feature (Needs Parsing) | None. Text parser required to extract clean integer BHK. |
| `society` | Categorical (String) | Housing complex / gated society identifier | Society code / name | `"Coomee "` | 41.31% (5,502) | High-Cardinality Feature | Low direct leakage, but high missingness requires categorical imputation. |
| `total_sqft` | Categorical / String | Raw area string with mixed formats | Mixed (`1200`, `2100 - 2850`, `34.46Sq. Meter`) | `"1056"` | 0.0% (0) | Physical Dimension | None, but requires regex normalization to numerical sqft. |
| `bath` | Numeric (Float) | Number of bathrooms | Count | `2.0` | 0.55% (73) | Feature (Predictor) | None. Baseline contract feature. |
| `balcony` | Numeric (Float) | Number of balconies | Count | `2.0` | 4.57% (609) | Feature (Predictor) | None. Baseline contract feature. |
| `price` | Numeric (Float) | Estimated total property price | Lakhs Indian Rupees | `72.0` | 0.0% (0) | **Target Variable ($y$)** | Target output for Bengaluru sub-engine. |

---

## 3. National Rental Dataset (`india_house_rent.csv`)

| Field Name | Type | Meaning / Definition | Unit | Example Value | Missingness | Expected Usage | Leakage Risk / Audit Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Posted On` | Temporal (Date) | Date listing was published | `YYYY-MM-DD` | `"2022-05-18"` | 0.0% (0) | Temporal Feature / Filter | None. Allows temporal stratification (Q2 2022). |
| `BHK` | Numeric (Integer) | Bedroom layout | Count | `2` | 0.0% (0) | Feature (Predictor) | None. Core layout variable. |
| `Rent` | Numeric (Float) | Monthly rental valuation | Indian Rupees (INR / month) | `16000.0` | 0.0% (0) | **Rental Target Variable** | Target for Rental Yield Engine. Exclude from capital price engine. |
| `Size` | Numeric (Float) | Total property floor size | Square Feet (sqft) | `850.0` | 0.0% (0) | Feature (Predictor) | None. Continuous area metric. |
| `Floor` | Categorical (String) | Floor level and total building floors | Text string (`"1 out of 3"`, `"Ground out of 2"`) | `"2 out of 4"` | 0.0% (0) | Feature (Needs Parsing) | None. Can be parsed into `floor_num` and `total_floors`. |
| `Area Type` | Categorical (String) | Floor calculation method | Category (`Super Area`, `Carpet Area`, `Built Area`) | `"Carpet Area"` | 0.0% (0) | Feature (Predictor) | None. Standard real-estate categorization. |
| `Area Locality` | Categorical (String) | Locality / neighborhood name | Locality string | `"Salt Lake City Sector 2"` | 0.0% (0) | Spatial Feature | None. High locality density in 6 Tier-1 Metros. |
| `City` | Categorical (String) | Metropolitan municipality | City string (`Mumbai`, `Bangalore`, `Delhi`, etc.) | `"Mumbai"` | 0.0% (0) | Geographic Scope | None. 100% matched with 6 major baseline metros. |
| `Furnishing Status`| Categorical (String) | Fit-out condition | Category (`Furnished`, `Semi-Furnished`, `Unfurnished`) | `"Semi-Furnished"` | 0.0% (0) | Feature (Predictor) | None. Direct 1:1 match with baseline contract. |
| `Tenant Preferred` | Categorical (String) | Landlord preference | Category (`Bachelors/Family`, `Family`, `Bachelors`) | `"Bachelors/Family"` | 0.0% (0) | Future Intelligence | None. Tenant matching and rental liquidity metric. |
| `Bathroom` | Numeric (Float) | Bathroom count | Count | `2.0` | 0.0% (0) | Feature (Predictor) | None. Direct baseline match. |
| `Point of Contact`| Categorical (String) | Entity contact channel | Category (`Contact Owner`, `Contact Agent`, `Contact Builder`) | `"Contact Owner"` | 0.0% (0) | Market Profile | None. Useful for disintermediation analytics. |

---

## 4. Delhi NCR Micro-Market Dataset (`delhi_magicbricks_flats.csv`)

| Field Name | Type | Meaning / Definition | Unit | Example Value | Missingness | Expected Usage | Leakage Risk / Audit Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Area` | Numeric (Float) | Total area of flat | Square Feet (sqft) | `1200.0` | 0.0% (0) | Feature (Predictor) | None. |
| `BHK` | Numeric (Integer) | Bedroom count | Count | `3` | 0.0% (0) | Feature (Predictor) | None. |
| `Bathroom` | Numeric (Float) | Bathroom count | Count | `2.0` | 0.16% (2) | Feature (Predictor) | None. |
| `Furnishing` | Categorical (String) | Furnishing status | Category (`Semi-Furnished`, `Furnished`, `Unfurnished`) | `"Semi-Furnished"` | 0.40% (5) | Feature (Predictor) | None. Direct baseline match. |
| `Locality` | Categorical (String) | Micro-market locality in Delhi | Locality name | `"Lajpat Nagar 3"` | 0.0% (0) | Spatial Feature | None. 365 Delhi NCR sub-markets. |
| `Parking` | Numeric (Float) | Reserved parking spaces | Count | `1.0` | 2.62% (33) | Feature (Predictor) | None. Highly informative physical amenity for metro living. |
| `Price` | Numeric (Float) | Property sale valuation | Indian Rupees (INR) | `14200000.0` | 0.0% (0) | **Target Variable ($y$)** | Capital property valuation target in full INR. |
| `Status` | Categorical (String) | Construction status | Category (`Ready_to_move`, `Almost_ready`) | `"Ready_to_move"` | 0.0% (0) | Feature (Predictor) | None. Corresponds to baseline `Status`. |
| `Transaction` | Categorical (String) | Market channel | Category (`Resale`, `New_Property`) | `"Resale"` | 0.0% (0) | Feature (Predictor) | None. Direct match with baseline `Transaction`. |
| `Type` | Categorical (String) | Building architectural typology | Category (`Builder_Floor`, `Apartment`) | `"Builder_Floor"` | 0.40% (5) | Feature (Predictor) | None. Differentiates standalone floors vs high-rise units. |
| `Per_Sqft` | Numeric (Float) | Rate per square foot | INR / sqft | `11833.0` | 19.14% (241) | **FORBIDDEN FEATURE** | **CRITICAL DIRECT TARGET LEAKAGE:** Derived via $\text{Price} / \text{Area}$. Must NEVER be used as a predictor. |

---

## 5. Protected Baseline 11-Feature Contract Reference

| Contract Feature | Type | Valid Range / Categories | Mapping to New Datasets |
| :--- | :--- | :--- | :--- |
| `area_sqft` | `float` (>0, $\le 50,000$) | `SQUARE_FT`, `total_sqft`, `Size`, `Area` |
| `bhk` | `int` (1 to 20) | `BHK_NO.`, `size` (parsed), `BHK` |
| `bathroom` | `float` (1 to 20) | `bath`, `Bathroom` |
| `balcony` | `float` (0 to 20) | `balcony`, default $1.0$ |
| `floor_num` | `float` (-5 to 200) | `Floor` (parsed), default $1.0$ |
| `total_floors` | `float` (1 to 200) | `Floor` (parsed), default $10.0$ |
| `location` | `str` (Verified City) | `ADDRESS` (parsed city), `City`, `location`, `Locality` |
| `Furnishing` | `str` (`Furnished`, `Semi-Furnished`, `Unfurnished`) | `Furnishing Status`, `Furnishing` |
| `Transaction` | `str` (`Resale`, `New Property`, `Other`) | `RESALE`, `Transaction` |
| `facing` | `str` (`East`, `North`, `West`, `South`, etc.) | Default `"East"` when missing |
| `Ownership` | `str` (`Freehold`, `Leasehold`, etc.) | Default `"Freehold"` when missing |
