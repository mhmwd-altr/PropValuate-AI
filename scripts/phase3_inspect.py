import os
import joblib
import pandas as pd
import numpy as np
import sklearn

def main():
    print(f"Scikit-Learn Version: {sklearn.__version__}")
    print(f"Pandas Version: {pd.__version__}")
    print(f"NumPy Version: {np.__version__}")

    # 1. Inspect existing model
    model_path = os.path.join("backend", "models", "house_price.pkl")
    if os.path.exists(model_path):
        model_obj = joblib.load(model_path)
        print(f"\nExisting Model: {model_path} ({os.path.getsize(model_path)/1024:.2f} KB)")
        print(f"  Type: {type(model_obj)}")
        if hasattr(model_obj, "named_steps"):
            print(f"  Pipeline steps: {list(model_obj.named_steps.keys())}")
            pre = model_obj.named_steps.get("preprocessor")
            reg = model_obj.named_steps.get("regressor")
            print(f"  Regressor: {type(reg).__name__}")
            if hasattr(pre, "transformers_"):
                print("  Transformers:")
                for name, trans, cols in pre.transformers_:
                    print(f"    - {name}: {type(trans).__name__} on {cols}")

    # 2. Inspect Primary Training Dataset
    train_path = os.path.join("data", "raw", "india_housing_challenge_train.csv")
    df = pd.read_csv(train_path)
    print(f"\nPrimary Training Dataset: {train_path}")
    print(f"  Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Missing values: {df.isnull().sum().sum()}")
    print(f"  Exact duplicates: {df.duplicated().sum()}")
    
    target_col = "TARGET(PRICE_IN_LACS)"
    print(f"  Target summary ({target_col}):")
    print(f"    Min:    Rs. {df[target_col].min():.2f} Lakhs (Rs. {df[target_col].min()*100000:,.0f} INR)")
    print(f"    P25:    Rs. {df[target_col].quantile(0.25):.2f} Lakhs (Rs. {df[target_col].quantile(0.25)*100000:,.0f} INR)")
    print(f"    Median: Rs. {df[target_col].median():.2f} Lakhs (Rs. {df[target_col].median()*100000:,.0f} INR)")
    print(f"    P75:    Rs. {df[target_col].quantile(0.75):.2f} Lakhs (Rs. {df[target_col].quantile(0.75)*100000:,.0f} INR)")
    print(f"    P99:    Rs. {df[target_col].quantile(0.99):.2f} Lakhs (Rs. {df[target_col].quantile(0.99)*100000:,.0f} INR)")
    print(f"    Max:    Rs. {df[target_col].max():.2f} Lakhs (Rs. {df[target_col].max()*100000:,.0f} INR)")
    print(f"    Mean:   Rs. {df[target_col].mean():.2f} Lakhs (Rs. {df[target_col].mean()*100000:,.0f} INR)")
    print(f"    Std:    Rs. {df[target_col].std():.2f} Lakhs")

    # 3. Inspect Features
    print("\nFeature Distributions:")
    print("  POSTED_BY:", df["POSTED_BY"].value_counts().to_dict())
    print("  UNDER_CONSTRUCTION:", df["UNDER_CONSTRUCTION"].value_counts().to_dict())
    print("  RERA:", df["RERA"].value_counts().to_dict())
    print("  BHK_NO:", df["BHK_NO."].value_counts().head(8).to_dict())
    print("  BHK_OR_RK:", df["BHK_OR_RK"].value_counts().to_dict())
    print("  READY_TO_MOVE:", df["READY_TO_MOVE"].value_counts().to_dict())
    print("  RESALE:", df["RESALE"].value_counts().to_dict())
    print(f"  SQUARE_FT: min={df['SQUARE_FT'].min()}, median={df['SQUARE_FT'].median()}, mean={df['SQUARE_FT'].mean():.1f}, p99={df['SQUARE_FT'].quantile(0.99):.1f}, max={df['SQUARE_FT'].max()}")

if __name__ == "__main__":
    main()
