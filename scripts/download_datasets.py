import urllib.request
import os
import hashlib
import json
import pandas as pd

DATASETS = {
    "india_housing_challenge_train.csv": {
        "url": "https://raw.githubusercontent.com/srikanth2102/Predict-the-house-prices-in-India/master/train.csv",
        "description": "National multi-city property transaction challenge dataset with geo coordinates"
    },
    "bengaluru_house_prices.csv": {
        "url": "https://raw.githubusercontent.com/codebasics/py/master/DataScience/BangloreHomePrices/model/bengaluru_house_prices.csv",
        "description": "Bengaluru metro real estate pricing and locality dataset"
    },
    "india_house_rent.csv": {
        "url": "https://raw.githubusercontent.com/Athulyachandran/House-Rent-Dataset-Analysis/main/House_Rent_Dataset.csv",
        "description": "Rental market listings across 6 Indian Tier-1 metropolitan centers"
    },
    "delhi_magicbricks_flats.csv": {
        "url": "https://raw.githubusercontent.com/Gaurav-223344/Delhi-House-Price-Prediction/master/MagicBricks.csv",
        "description": "Delhi NCR micro-market residential flat listings"
    }
}

def main():
    raw_dir = os.path.join("data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    meta_dir = os.path.join("data", "metadata")
    os.makedirs(meta_dir, exist_ok=True)

    manifest = {}

    for filename, info in DATASETS.items():
        filepath = os.path.join(raw_dir, filename)
        url = info["url"]
        print(f"Downloading {filename} from {url}...")
        
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp, open(filepath, "wb") as out_file:
            content = resp.read()
            out_file.write(content)
        
        file_size = os.path.getsize(filepath)
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            hasher.update(f.read())
        sha256 = hasher.hexdigest()

        df = pd.read_csv(filepath)
        
        manifest[filename] = {
            "filename": filename,
            "url": url,
            "description": info["description"],
            "size_bytes": file_size,
            "size_kb": round(file_size / 1024, 2),
            "rows": int(len(df)),
            "columns_count": int(len(df.columns)),
            "columns": list(df.columns),
            "sha256": sha256
        }
        print(f"  [OK] {filename}: {len(df)} rows, {len(df.columns)} cols, {round(file_size/1024, 2)} KB")

    manifest_path = os.path.join(meta_dir, "raw_datasets_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest successfully written to {manifest_path}")

if __name__ == "__main__":
    main()
