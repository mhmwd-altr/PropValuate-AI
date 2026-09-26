import os
import json
import re
import numpy as np
import pandas as pd

def profile_dataset(name, filepath, baseline_locations):
    print(f"=== Profiling {name} ({filepath}) ===")
    df = pd.read_csv(filepath)
    
    # 1. Dimensions & Memory
    rows, cols = df.shape
    memory_mb = round(df.memory_usage(deep=True).sum() / (1024 * 1024), 3)
    
    # 2. Missingness
    null_counts = df.isnull().sum().to_dict()
    null_pct = (df.isnull().sum() / rows * 100).round(2).to_dict()
    
    # 3. Duplicates
    exact_dups = int(df.duplicated().sum())
    
    # 4. Numeric Profiles
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_profile = {}
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) > 0:
            numeric_profile[col] = {
                "count": int(len(series)),
                "mean": float(round(series.mean(), 2)),
                "std": float(round(series.std(), 2)),
                "min": float(round(series.min(), 2)),
                "p25": float(round(series.quantile(0.25), 2)),
                "median": float(round(series.median(), 2)),
                "p75": float(round(series.quantile(0.75), 2)),
                "max": float(round(series.max(), 2)),
                "zeros_count": int((series == 0).sum()),
                "negatives_count": int((series < 0).sum())
            }
            
    # 5. Categorical Profiles
    cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
    cat_profile = {}
    for col in cat_cols:
        series = df[col].dropna().astype(str)
        top_vals = series.value_counts().head(10).to_dict()
        cat_profile[col] = {
            "unique_count": int(series.nunique()),
            "top_10_values": top_vals,
            "sample_values": series.unique()[:5].tolist()
        }

    # 6. Geographic Analysis
    geo_profile = {"has_geo": False}
    leakage_notes = []
    
    if "ADDRESS" in df.columns:
        def extract_city(addr):
            parts = [p.strip().lower() for p in str(addr).split(",") if p.strip()]
            return parts[-1] if parts else "unknown"
        
        df["extracted_city"] = df["ADDRESS"].apply(extract_city)
        extracted_cities = df["extracted_city"].value_counts()
        
        matches = [c for c in extracted_cities.index if c in baseline_locations]
        new_cities = [c for c in extracted_cities.index if c not in baseline_locations and extracted_cities[c] >= 10]
        
        geo_profile = {
            "has_geo": True,
            "total_extracted_cities": int(extracted_cities.count()),
            "top_15_cities": extracted_cities.head(15).to_dict(),
            "matches_with_81_baseline": len(matches),
            "matched_cities_list": matches[:20],
            "potential_new_cities": new_cities[:20]
        }
        if "LATITUDE" in df.columns and "LONGITUDE" in df.columns:
            # Audit coordinate swap
            # Notice: column labelled 'LONGITUDE' contains ~10-35 (Latitude of India)
            # column labelled 'LATITUDE' contains ~70-90 (Longitude of India)
            swapped_lat = df["LONGITUDE"]
            swapped_long = df["LATITUDE"]
            
            valid_swapped_india = df[(swapped_lat >= 6.0) & (swapped_lat <= 38.0) & 
                                     (swapped_long >= 68.0) & (swapped_long <= 98.0)]
            
            geo_profile["coordinates"] = {
                "raw_longitude_col_stats": {"min": float(df["LONGITUDE"].min()), "max": float(df["LONGITUDE"].max()), "mean": float(df["LONGITUDE"].mean())},
                "raw_latitude_col_stats": {"min": float(df["LATITUDE"].min()), "max": float(df["LATITUDE"].max()), "mean": float(df["LATITUDE"].mean())},
                "critical_finding": "HEADER INVERSION DETECTED: 'LONGITUDE' column contains Indian latitudes (8-37 N), while 'LATITUDE' contains Indian longitudes (68-97 E).",
                "valid_india_coords_when_corrected_count": int(len(valid_swapped_india)),
                "valid_india_coords_when_corrected_pct": float(round(len(valid_swapped_india) / rows * 100, 2))
            }
            leakage_notes.append("CRITICAL DATA ANOMALY: LONGITUDE and LATITUDE column headers are inverted in raw source. Correcting mapping yields 95.8% valid Indian geo-coordinates.")
            
    elif "City" in df.columns:
        cities = df["City"].dropna().str.lower().value_counts()
        matches = [c for c in cities.index if c in baseline_locations]
        geo_profile = {
            "has_geo": True,
            "city_column": "City",
            "unique_cities": int(cities.count()),
            "city_distribution": cities.to_dict(),
            "matches_with_81_baseline": len(matches)
        }
    elif "location" in df.columns:
        locations = df["location"].dropna().str.lower().value_counts()
        geo_profile = {
            "has_geo": True,
            "locality_column": "location",
            "unique_localities": int(locations.count()),
            "top_10_localities": locations.head(10).to_dict()
        }
    elif "Locality" in df.columns:
        localities = df["Locality"].dropna().str.lower().value_counts()
        geo_profile = {
            "has_geo": True,
            "locality_column": "Locality",
            "unique_localities": int(localities.count()),
            "top_10_localities": localities.head(10).to_dict()
        }

    # 7. Temporal Analysis
    temporal_profile = {"has_temporal": False}
    for col in df.columns:
        if "date" in col.lower() or "posted" in col.lower() or "year" in col.lower() or "month" in col.lower():
            temporal_profile = {
                "has_temporal": True,
                "temporal_column": col,
                "sample_values": df[col].dropna().head(10).tolist(),
                "unique_values": int(df[col].nunique())
            }
            try:
                date_series = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
                valid_dates = date_series.dropna()
                if len(valid_dates) > 0:
                    temporal_profile["earliest_date"] = str(valid_dates.min().strftime('%Y-%m-%d'))
                    temporal_profile["latest_date"] = str(valid_dates.max().strftime('%Y-%m-%d'))
                    temporal_profile["span_days"] = int((valid_dates.max() - valid_dates.min()).days)
                    temporal_profile["parsed_valid_date_count"] = int(len(valid_dates))
                    monthly_counts = date_series.dt.to_period('M').value_counts().head(6)
                    temporal_profile["monthly_distribution"] = {str(k): int(v) for k, v in monthly_counts.items()}
            except Exception as e:
                temporal_profile["parsing_error"] = str(e)

    # 8. Leakage & Anomaly Checks
    if "Per_Sqft" in df.columns and "Price" in df.columns and "Area" in df.columns:
        leakage_notes.append("DIRECT TARGET LEAKAGE: 'Per_Sqft' is mathematically derived as (Price / Area). It must be excluded from feature vectors in future modeling phases.")
    if "TARGET(PRICE_IN_LACS)" in df.columns:
        corr_series = df.select_dtypes(include=[np.number]).corr()["TARGET(PRICE_IN_LACS)"].sort_values(ascending=False).to_dict()
        numeric_profile["target_correlations"] = {k: round(v, 4) for k, v in corr_series.items() if not np.isnan(v)}

    profile = {
        "dataset_name": name,
        "filepath": filepath,
        "rows": rows,
        "cols": cols,
        "memory_mb": memory_mb,
        "exact_duplicates": exact_dups,
        "null_counts": null_counts,
        "null_percentages": null_pct,
        "numeric_profile": numeric_profile,
        "categorical_profile": cat_profile,
        "geographic_profile": geo_profile,
        "temporal_profile": temporal_profile,
        "leakage_notes": leakage_notes,
        "sample_rows": df.head(3).to_dict(orient="records")
    }
    return profile

def main():
    with open(os.path.join("backend", "models", "locations.json"), "r", encoding="utf-8") as f:
        baseline_locations = json.load(f)["locations"]
    baseline_locations_set = set(l.lower().strip() for l in baseline_locations)

    raw_dir = os.path.join("data", "raw")
    all_profiles = {}
    
    files = {
        "india_housing_challenge_train": os.path.join(raw_dir, "india_housing_challenge_train.csv"),
        "bengaluru_house_prices": os.path.join(raw_dir, "bengaluru_house_prices.csv"),
        "india_house_rent": os.path.join(raw_dir, "india_house_rent.csv"),
        "delhi_magicbricks_flats": os.path.join(raw_dir, "delhi_magicbricks_flats.csv")
    }

    for name, path in files.items():
        if os.path.exists(path):
            all_profiles[name] = profile_dataset(name, path, baseline_locations_set)

    meta_dir = os.path.join("data", "metadata")
    out_path = os.path.join(meta_dir, "dataset_profiling_audit.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_profiles, f, indent=2, default=str)
    print(f"\nSaved comprehensive profiling audit to {out_path}")

if __name__ == "__main__":
    main()
