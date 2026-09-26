import os
import json
import hashlib
import pandas as pd

def update_manifest():
    meta_dir = os.path.join("data", "metadata")
    raw_dir = os.path.join("data", "raw")
    os.makedirs(meta_dir, exist_ok=True)

    files = sorted([f for f in os.listdir(raw_dir) if f.endswith(".csv")])
    manifest = {}

    for f in files:
        fpath = os.path.join(raw_dir, f)
        df = pd.read_csv(fpath)
        size_bytes = os.path.getsize(fpath)
        sha256 = hashlib.sha256(open(fpath, "rb").read()).hexdigest()
        manifest[f] = {
            "filename": f,
            "rows": int(len(df)),
            "cols": int(len(df.columns)),
            "size_bytes": size_bytes,
            "size_kb": round(size_bytes / 1024, 2),
            "sha256": sha256,
            "columns": list(df.columns)
        }

    manifest_path = os.path.join(meta_dir, "raw_datasets_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as out:
        json.dump(manifest, out, indent=2)

    print(f"Updated {manifest_path} with {len(manifest)} datasets:")
    for k, v in manifest.items():
        print(f"  {k:38s}: {v['rows']:>6} rows x {v['cols']:>2} cols ({v['size_kb']:>7.1f} KB)")

if __name__ == "__main__":
    update_manifest()
