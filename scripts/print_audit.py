import json

with open("data/metadata/dataset_profiling_audit.json", "r", encoding="utf-8") as f:
    audit = json.load(f)

for name, d in audit.items():
    print("=" * 70)
    print(f"DATASET: {name}")
    print(f"  Shape: {d['rows']} rows x {d['cols']} columns | Memory: {d['memory_mb']} MB | Duplicates: {d['exact_duplicates']}")
    nulls = {k: v for k, v in d['null_counts'].items() if v > 0}
    print(f"  Nulls: {nulls if nulls else 'Zero missing values'}")
    
    print("  Numeric Variables Summary:")
    for col, n in d['numeric_profile'].items():
        if col != 'target_correlations':
            print(f"    - {col:25s}: min={n['min']:<10} median={n['median']:<10} mean={n['mean']:<10} max={n['max']:<10}")
            
    print("  Categorical Variables:")
    for col, c in d['categorical_profile'].items():
        print(f"    - {col:25s}: {c['unique_count']} unique | sample: {c['sample_values'][:3]}")
        
    print(f"  Geographic Profile:")
    gp = d['geographic_profile']
    for k, v in gp.items():
        print(f"    - {k}: {v}")
        
    print(f"  Temporal Profile: {d['temporal_profile']}")
    print(f"  Leakage Notes: {d['leakage_notes']}")
