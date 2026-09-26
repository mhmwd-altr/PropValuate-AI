import os
import sys
import json
import time
import math
import hashlib
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, KFold, GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder, FunctionTransformer
from sklearn.linear_model import Ridge
from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor
)
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Fixed Random Seed for Complete Reproducibility
RANDOM_SEED = 42

# Major Indian Metro Coordinates for Spatial Distance Proxies
METRO_CENTERS = {
    "mumbai": (18.9220, 72.8347),
    "delhi": (28.6304, 77.2177),
    "bangalore": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639)
}

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculates great circle distance in km between two coordinate pairs."""
    r = 6371.0  # Earth radius in km
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    
    a = (np.sin(delta_phi / 2.0) ** 2 +
         np.cos(phi1) * np.cos(phi2) * (np.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    return r * c

def extract_city(address_str):
    if not isinstance(address_str, str):
        return "unknown"
    parts = [p.strip().lower() for p in address_str.split(",") if p.strip()]
    return parts[-1] if parts else "unknown"

def extract_locality(address_str):
    if not isinstance(address_str, str):
        return "unknown"
    parts = [p.strip().lower() for p in address_str.split(",") if p.strip()]
    return parts[0] if parts else "unknown"

def load_and_preprocess_data(csv_path):
    print(f"Loading raw primary data from: {csv_path}")
    raw_df = pd.read_csv(csv_path)
    initial_count = len(raw_df)
    
    # 1. Exact Deduplication
    df = raw_df.drop_duplicates().copy()
    dup_count = initial_count - len(df)
    print(f"Deduplication: {initial_count} raw rows -> {len(df)} unique rows (removed {dup_count} exact duplicates)")
    
    # 2. Correct Coordinate Header Inversion
    # In raw file: 'LONGITUDE' contains Latitudes (8-37 N), 'LATITUDE' contains Longitudes (68-97 E)
    df["latitude"] = df["LONGITUDE"]
    df["longitude"] = df["LATITUDE"]
    
    # 3. Standardize Feature Names
    df["area_sqft"] = df["SQUARE_FT"].astype(float)
    df["bhk"] = df["BHK_NO."].astype(int)
    df["bhk_or_rk"] = df["BHK_OR_RK"].astype(str)
    df["rera"] = df["RERA"].astype(int)
    df["posted_by"] = df["POSTED_BY"].astype(str)
    df["under_construction"] = df["UNDER_CONSTRUCTION"].astype(int)
    df["ready_to_move"] = df["READY_TO_MOVE"].astype(int)
    df["resale"] = df["RESALE"].astype(int)
    df["city"] = df["ADDRESS"].apply(extract_city)
    df["locality"] = df["ADDRESS"].apply(extract_locality)
    
    # Target in Lakhs and INR
    df["price_lakhs"] = df["TARGET(PRICE_IN_LACS)"].astype(float)
    df["price_inr"] = df["price_lakhs"] * 100000.0
    
    # 4. Filter Physical and Coordinate Outliers
    # Keep valid India bounding box and plausible residential unit parameters
    valid_mask = (
        (df["latitude"] >= 6.0) & (df["latitude"] <= 38.0) &
        (df["longitude"] >= 68.0) & (df["longitude"] <= 98.0) &
        (df["area_sqft"] >= 100.0) & (df["area_sqft"] <= 15000.0) &
        (df["bhk"] >= 1) & (df["bhk"] <= 10) &
        (df["price_lakhs"] >= 1.0) & (df["price_lakhs"] <= 5000.0)
    )
    
    cleaned_df = df[valid_mask].copy()
    filtered_out = len(df) - len(cleaned_df)
    print(f"Domain & Geo Filtering: {len(df)} rows -> {len(cleaned_df)} rows (filtered {filtered_out} out-of-bounds/outliers, {len(cleaned_df)/len(df)*100:.2f}% retained)")
    
    # 5. Spatial Distance Feature Engineering
    for metro, (m_lat, m_lon) in METRO_CENTERS.items():
        cleaned_df[f"dist_{metro}_km"] = haversine_distance(
            cleaned_df["latitude"].values, cleaned_df["longitude"].values, m_lat, m_lon
        )
    
    dist_cols = [f"dist_{m}_km" for m in METRO_CENTERS.keys()]
    cleaned_df["dist_nearest_metro_km"] = cleaned_df[dist_cols].min(axis=1)
    
    # Area per room proxy
    cleaned_df["area_per_bhk"] = cleaned_df["area_sqft"] / (cleaned_df["bhk"] + 0.1)
    cleaned_df["is_rk"] = (cleaned_df["bhk_or_rk"] == "RK").astype(int)
    
    # Frequency encode rare cities: keep top 50 cities, group rest as 'other'
    top_cities = set(cleaned_df["city"].value_counts().head(50).index)
    cleaned_df["city_grouped"] = cleaned_df["city"].apply(lambda c: c if c in top_cities else "other")
    
    return cleaned_df

def compute_metrics(y_true_inr, y_pred_inr):
    y_true = np.array(y_true_inr, dtype=float)
    y_pred = np.maximum(np.array(y_pred_inr, dtype=float), 10000.0)  # floor at Rs 10k
    
    mae_inr = mean_absolute_error(y_true, y_pred)
    mae_lakhs = mae_inr / 100000.0
    rmse_inr = math.sqrt(mean_squared_error(y_true, y_pred))
    rmse_lakhs = rmse_inr / 100000.0
    r2 = r2_score(y_true, y_pred)
    
    # Percentage Errors
    pct_errors = np.abs((y_true - y_pred) / y_true) * 100.0
    mdape = float(np.median(pct_errors))
    mape = float(np.mean(pct_errors))
    
    return {
        "mae_inr": float(round(mae_inr, 2)),
        "mae_lakhs": float(round(mae_lakhs, 2)),
        "rmse_inr": float(round(rmse_inr, 2)),
        "rmse_lakhs": float(round(rmse_lakhs, 2)),
        "r2": float(round(r2, 4)),
        "mdape_pct": float(round(mdape, 2)),
        "mape_pct": float(round(mape, 2))
    }

def main():
    print("=" * 80)
    print("PHASE 3 — VALUATION ENGINE V2: EXPERIMENTATION & MULTI-MODEL BENCHMARK")
    print("=" * 80)
    
    data_path = os.path.join("data", "raw", "india_housing_challenge_train.csv")
    df = load_and_preprocess_data(data_path)
    
    # Define Feature Sets
    numeric_features = [
        "area_sqft", "bhk", "is_rk", "rera", "under_construction", "ready_to_move", "resale",
        "latitude", "longitude", "area_per_bhk", "dist_nearest_metro_km",
        "dist_mumbai_km", "dist_delhi_km", "dist_bangalore_km"
    ]
    categorical_features = ["posted_by", "city_grouped"]
    
    all_feature_cols = numeric_features + categorical_features
    X = df[all_feature_cols]
    y = df["price_inr"]  # Training directly on standard INR target
    cities = df["city_grouped"]
    
    print(f"\nFinal Feature Matrix: {X.shape[0]} samples x {X.shape[1]} features")
    print(f"Numeric features ({len(numeric_features)}): {numeric_features}")
    print(f"Categorical features ({len(categorical_features)}): {categorical_features}")
    
    # Train / Test Split (80% / 20%)
    X_train, X_test, y_train, y_test, cities_train, cities_test = train_test_split(
        X, y, cities, test_size=0.20, random_state=RANDOM_SEED
    )
    print(f"\nHoldout Split: Train = {X_train.shape[0]} samples, Test = {X_test.shape[0]} samples")
    
    # Preprocessor Construction
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features)
        ],
        remainder="drop"
    )
    
    # Candidate Models Suite
    models_to_test = {
        "Ridge Regression": Ridge(alpha=100.0, random_state=RANDOM_SEED),
        "Random Forest (100 Trees)": RandomForestRegressor(n_estimators=100, max_depth=20, min_samples_split=5, random_state=RANDOM_SEED, n_jobs=-1),
        "Extra Trees (100 Trees)": ExtraTreesRegressor(n_estimators=100, max_depth=20, min_samples_split=5, random_state=RANDOM_SEED, n_jobs=-1),
        "Gradient Boosting (150 Trees)": GradientBoostingRegressor(n_estimators=150, max_depth=6, learning_rate=0.08, random_state=RANDOM_SEED),
        "HistGradientBoosting (Standard)": HistGradientBoostingRegressor(max_iter=250, max_depth=12, learning_rate=0.08, l2_regularization=1.0, random_state=RANDOM_SEED),
        "HistGradientBoosting (Log-Target)": TransformedTargetRegressor(
            regressor=HistGradientBoostingRegressor(max_iter=300, max_depth=12, learning_rate=0.06, l2_regularization=2.0, random_state=RANDOM_SEED),
            func=np.log1p,
            inverse_func=np.expm1
        )
    }
    
    results = {}
    cv_kf = KFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    
    print("\n" + "=" * 80)
    print("RUNNING MULTI-MODEL EXPERIMENTS (5-FOLD CV & HOLDOUT TEST)")
    print("=" * 80)
    
    for name, reg in models_to_test.items():
        t0 = time.time()
        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", reg)
        ])
        
        # 1. 5-Fold Cross Validation on Train Split
        cv_r2_scores = []
        cv_mae_lakhs = []
        
        for fold, (train_idx, val_idx) in enumerate(cv_kf.split(X_train)):
            X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
            y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]
            
            pipeline.fit(X_tr, y_tr)
            y_val_pred = pipeline.predict(X_val)
            val_metrics = compute_metrics(y_val, y_val_pred)
            cv_r2_scores.append(val_metrics["r2"])
            cv_mae_lakhs.append(val_metrics["mae_lakhs"])
            
        mean_cv_r2 = float(round(np.mean(cv_r2_scores), 4))
        std_cv_r2 = float(round(np.std(cv_r2_scores), 4))
        mean_cv_mae = float(round(np.mean(cv_mae_lakhs), 2))
        
        # 2. Fit on Full Train Set & Evaluate on Holdout Test Set
        pipeline.fit(X_train, y_train)
        y_train_pred = pipeline.predict(X_train)
        y_test_pred = pipeline.predict(X_test)
        
        train_metrics = compute_metrics(y_train, y_train_pred)
        test_metrics = compute_metrics(y_test, y_test_pred)
        elapsed_sec = round(time.time() - t0, 2)
        
        results[name] = {
            "model_name": name,
            "training_time_sec": elapsed_sec,
            "cv_5fold_r2_mean": mean_cv_r2,
            "cv_5fold_r2_std": std_cv_r2,
            "cv_5fold_mae_lakhs": mean_cv_mae,
            "train_r2": train_metrics["r2"],
            "train_mae_lakhs": train_metrics["mae_lakhs"],
            "test_r2": test_metrics["r2"],
            "test_mae_lakhs": test_metrics["mae_lakhs"],
            "test_mae_inr": test_metrics["mae_inr"],
            "test_rmse_lakhs": test_metrics["rmse_lakhs"],
            "test_rmse_inr": test_metrics["rmse_inr"],
            "test_mdape_pct": test_metrics["mdape_pct"],
            "test_mape_pct": test_metrics["mape_pct"],
            "generalization_gap": round(train_metrics["r2"] - test_metrics["r2"], 4),
            "pipeline": pipeline,
            "test_predictions": y_test_pred
        }
        
        print(f"\n{name:35s} | Time: {elapsed_sec:>5.1f}s")
        print(f"  CV 5-Fold R2: {mean_cv_r2:.4f} (+/- {std_cv_r2:.4f}) | CV MAE: Rs. {mean_cv_mae:.2f} Lakhs")
        print(f"  Test R2:      {test_metrics['r2']:.4f} | Test MAE: Rs. {test_metrics['mae_lakhs']:.2f} Lakhs | Test RMSE: Rs. {test_metrics['rmse_lakhs']:.2f} Lakhs")
        print(f"  Test MdAPE:   {test_metrics['mdape_pct']:.2f}% | Gen Gap (R2_tr - R2_te): {train_metrics['r2'] - test_metrics['r2']:.4f}")

    # 3. Geographic Generalization Experiment (GroupKFold on Municipalities)
    print("\n" + "=" * 80)
    print("EXPERIMENT C: GEOGRAPHIC GENERALIZATION (GROUP-K-FOLD ON CITIES)")
    print("=" * 80)
    
    gkf = GroupKFold(n_splits=5)
    geo_results = {}
    
    top_models = ["HistGradientBoosting (Standard)", "Random Forest (100 Trees)", "Extra Trees (100 Trees)"]
    for name in top_models:
        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", models_to_test[name])
        ])
        geo_r2s = []
        geo_maes = []
        for fold, (g_train_idx, g_val_idx) in enumerate(gkf.split(X, y, groups=cities)):
            X_gtr, X_gval = X.iloc[g_train_idx], X.iloc[g_val_idx]
            y_gtr, y_gval = y.iloc[g_train_idx], y.iloc[g_val_idx]
            pipeline.fit(X_gtr, y_gtr)
            y_gval_pred = pipeline.predict(X_gval)
            g_m = compute_metrics(y_gval, y_gval_pred)
            geo_r2s.append(g_m["r2"])
            geo_maes.append(g_m["mae_lakhs"])
            
        geo_results[name] = {
            "geo_unseen_r2_mean": float(round(np.mean(geo_r2s), 4)),
            "geo_unseen_r2_std": float(round(np.std(geo_r2s), 4)),
            "geo_unseen_mae_lakhs": float(round(np.mean(geo_maes), 2))
        }
        print(f"{name:35s} | Unseen City R2: {np.mean(geo_r2s):.4f} (+/- {np.std(geo_r2s):.4f}) | Unseen City MAE: Rs. {np.mean(geo_maes):.2f} Lakhs")

    # 4. Detailed Error Analysis on Best Model (HistGradientBoosting Standard)
    best_candidate_name = "HistGradientBoosting (Standard)"
    best_result = results[best_candidate_name]
    best_pipeline = best_result["pipeline"]
    y_test_pred = best_result["test_predictions"]
    
    test_analysis_df = X_test.copy()
    test_analysis_df["actual_price_inr"] = y_test.values
    test_analysis_df["actual_price_lakhs"] = y_test.values / 100000.0
    test_analysis_df["predicted_price_inr"] = y_test_pred
    test_analysis_df["predicted_price_lakhs"] = y_test_pred / 100000.0
    test_analysis_df["abs_error_lakhs"] = np.abs(test_analysis_df["actual_price_lakhs"] - test_analysis_df["predicted_price_lakhs"])
    test_analysis_df["pct_error"] = np.abs((test_analysis_df["actual_price_inr"] - test_analysis_df["predicted_price_inr"]) / test_analysis_df["actual_price_inr"]) * 100.0
    
    # Segmented Price Tiers
    def get_price_tier(p_lakhs):
        if p_lakhs < 40.0:
            return "1. Affordable (< Rs 40L)"
        elif p_lakhs < 100.0:
            return "2. Mid-Market (Rs 40L - 1Cr)"
        elif p_lakhs < 300.0:
            return "3. Upper-Mid (Rs 1Cr - 3Cr)"
        else:
            return "4. Luxury (> Rs 3Cr)"
            
    test_analysis_df["price_tier"] = test_analysis_df["actual_price_lakhs"].apply(get_price_tier)
    tier_errors = test_analysis_df.groupby("price_tier").agg(
        count=("actual_price_lakhs", "count"),
        mean_actual=("actual_price_lakhs", "mean"),
        mae_lakhs=("abs_error_lakhs", "mean"),
        mdape_pct=("pct_error", "median"),
        mape_pct=("pct_error", "mean")
    ).round(2)
    
    # Segmented City Breakdown (Top Cities)
    city_errors = test_analysis_df.groupby("city_grouped").agg(
        count=("actual_price_lakhs", "count"),
        mae_lakhs=("abs_error_lakhs", "mean"),
        mdape_pct=("pct_error", "median")
    ).sort_values(by="count", ascending=False).head(15).round(2)
    
    print("\n" + "=" * 80)
    print("ERROR BREAKDOWN BY PRICE TIER (BEST CANDIDATE)")
    print("=" * 80)
    print(tier_errors.to_string())
    
    # 5. Save Artifacts & Model Registry
    os.makedirs("models", exist_ok=True)
    os.makedirs(os.path.join("models", "registry"), exist_ok=True)
    os.makedirs(os.path.join("backend", "models"), exist_ok=True)
    
    v2_artifact_path = os.path.join("backend", "models", "house_price_v2.pkl")
    joblib.dump(best_pipeline, v2_artifact_path)
    artifact_size_kb = round(os.path.getsize(v2_artifact_path) / 1024, 2)
    print(f"\nSaved Candidate V2 Artifact: {v2_artifact_path} ({artifact_size_kb} KB)")
    
    # Model Metadata
    v2_metadata = {
        "model_id": "propvaluate_valuation_v2",
        "model_version": "2.0.0",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "training_dataset": "india_housing_challenge_train.csv",
        "training_dataset_sha256": hashlib.sha256(open(data_path, "rb").read()).hexdigest(),
        "total_training_samples": int(len(df)),
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "algorithm": "HistGradientBoostingRegressor",
        "hyperparameters": {
            "max_iter": 250,
            "max_depth": 12,
            "learning_rate": 0.08,
            "l2_regularization": 1.0,
            "random_state": RANDOM_SEED
        },
        "feature_schema": {
            "numeric_features": numeric_features,
            "categorical_features": categorical_features,
            "total_features": len(all_feature_cols)
        },
        "metrics": {
            "test_r2": best_result["test_r2"],
            "test_mae_lakhs": best_result["test_mae_lakhs"],
            "test_mae_inr": best_result["test_mae_inr"],
            "test_rmse_lakhs": best_result["test_rmse_lakhs"],
            "test_rmse_inr": best_result["test_rmse_inr"],
            "test_mdape_pct": best_result["test_mdape_pct"],
            "cv_5fold_r2_mean": best_result["cv_5fold_r2_mean"],
            "cv_5fold_r2_std": best_result["cv_5fold_r2_std"],
            "cv_5fold_mae_lakhs": best_result["cv_5fold_mae_lakhs"],
            "geo_unseen_r2_mean": geo_results[best_candidate_name]["geo_unseen_r2_mean"],
            "geo_unseen_mae_lakhs": geo_results[best_candidate_name]["geo_unseen_mae_lakhs"]
        },
        "protected_baseline_comparison": {
            "baseline_r2": 0.7570,
            "baseline_mae_lakhs": 28.08,
            "baseline_rmse_lakhs": 67.38,
            "v2_r2_improvement": round(best_result["test_r2"] - 0.7570, 4),
            "v2_mae_improvement_lakhs": round(28.08 - best_result["test_mae_lakhs"], 2)
        }
    }
    
    registry_meta_path = os.path.join("models", "registry", "model_v2_metadata.json")
    with open(registry_meta_path, "w", encoding="utf-8") as f:
        json.dump(v2_metadata, f, indent=2)
    print(f"Saved Model V2 Metadata to {registry_meta_path}")
    
    # Save Full Multi-Model Comparison Summary JSON
    comparison_summary = []
    for name, r in results.items():
        comparison_summary.append({
            "model": name,
            "cv_r2": f"{r['cv_5fold_r2_mean']:.4f} +/- {r['cv_5fold_r2_std']:.4f}",
            "cv_mae_lakhs": r["cv_5fold_mae_lakhs"],
            "test_r2": r["test_r2"],
            "test_mae_lakhs": r["test_mae_lakhs"],
            "test_rmse_lakhs": r["test_rmse_lakhs"],
            "test_mdape_pct": r["test_mdape_pct"],
            "gen_gap": r["generalization_gap"],
            "geo_unseen_r2": geo_results.get(name, {}).get("geo_unseen_r2_mean", "N/A"),
            "training_time_sec": r["training_time_sec"]
        })
        
    summary_path = os.path.join("models", "registry", "multi_model_comparison.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(comparison_summary, f, indent=2)
    print(f"Saved Multi-Model Comparison to {summary_path}")

if __name__ == "__main__":
    main()
