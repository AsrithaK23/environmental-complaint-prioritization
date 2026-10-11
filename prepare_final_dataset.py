
import pandas as pd
from pathlib import Path

real_path = Path("dataset/processed/complaints_cleaned.csv")
synthetic_path = Path("dataset/raw/campus_synthetic_supplement_cleaned.csv")
output_path = Path("dataset/processed/complaints_final_for_person2.csv")

# Read the two prepared datasets
real = pd.read_csv(real_path)
synthetic = pd.read_csv(synthetic_path)

required = {"complaint_id", "complaint_text", "category", "source_type"}

for name, df in [("Real", real), ("Synthetic", synthetic)]:
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{name} dataset missing columns: {missing}")

# Combine without changing either input file
combined = pd.concat(
    [real[list(required)], synthetic[list(required)]],
    ignore_index=True
)

# Safety checks
if combined["complaint_id"].duplicated().any():
    raise ValueError("Duplicate complaint IDs found. Final dataset not saved.")

if combined[list(required)].isna().any().any():
    raise ValueError("Missing values found. Final dataset not saved.")

if combined["complaint_text"].astype(str).str.strip().eq("").any():
    raise ValueError("Blank complaints found. Final dataset not saved.")

# Preserve a consistent column order
combined = combined[
    ["complaint_id", "complaint_text", "category", "source_type"]
]

# Save to a NEW file
combined.to_csv(output_path, index=False)

print("Final dataset created:", output_path)
print("Total complaints:", len(combined))
print("\nCategory counts:")
print(combined["category"].value_counts().to_string())
print("\nSource counts:")
print(combined["source_type"].value_counts().to_string())
