
from pathlib import Path
import shutil
import pandas as pd

root = Path(__file__).resolve().parent

audit_path = root / "dataset/processed/real_label_audit_review.csv"
real_path = root / "dataset/processed/complaints_cleaned.csv"
synthetic_path = root / "dataset/raw/campus_synthetic_supplement_cleaned.csv"
final_path = root / "dataset/processed/complaints_final_for_person2.csv"

audit = pd.read_csv(audit_path, dtype=str, keep_default_na=False)
real = pd.read_csv(real_path, dtype=str, keep_default_na=False)
synthetic = pd.read_csv(synthetic_path, dtype=str, keep_default_na=False)

# Only use explicitly recorded CHANGE decisions.
changes = audit[
    (audit["manual_decision"] == "CHANGE")
    & (audit["corrected_category"] != "")
].copy()

# Verify the audit is complete before changing any dataset.
reviewed = audit["manual_decision"].isin(["KEEP", "CHANGE"])
assert reviewed.sum() == 245, "Expected all 245 audit decisions to be reviewed."
assert len(changes) == 100, (
    f"Expected 100 proposed changes, found {len(changes)}. "
    "Nothing has been changed."
)

valid_categories = {
    "Waste Management",
    "Water / Sanitation",
    "Air Pollution",
    "Noise Pollution",
    "Energy-related Issues",
    "Greenery / Landscaping",
    "Other",
}

assert set(changes["corrected_category"]).issubset(valid_categories)
assert changes["complaint_id"].is_unique
assert real["complaint_id"].is_unique
assert synthetic["complaint_id"].is_unique

# Confirm every correction refers to an existing real complaint.
real_ids = set(real["complaint_id"])
assert set(changes["complaint_id"]).issubset(real_ids), (
    "Some audited IDs are missing from the cleaned real dataset. "
    "Nothing has been changed."
)

# Apply corrections in memory first.
category_map = changes.set_index("complaint_id")["corrected_category"]
before = real.set_index("complaint_id")["category"].copy()
real["category"] = real["complaint_id"].map(category_map).fillna(
    real["category"]
)

actual_changed = int(
    (real.set_index("complaint_id")["category"] != before).sum()
)

# Rebuild the combined dataset in memory.
final = pd.concat([real, synthetic], ignore_index=True)

assert real["category"].isin(valid_categories).all()
assert synthetic["category"].isin(valid_categories).all()
assert not final.isna().any().any()
assert final["complaint_id"].is_unique
assert final["complaint_text"].str.strip().ne("").all()

normalized_text = final["complaint_text"].str.lower().str.strip()
assert not normalized_text.duplicated().any(), (
    "Duplicate complaint texts detected. Nothing has been written."
)

# Back up existing files before replacing them.
backup_real = real_path.with_name("complaints_cleaned.pre_audit_backup.csv")
backup_final = final_path.with_name("complaints_final.pre_audit_backup.csv")

if not backup_real.exists():
    shutil.copy2(real_path, backup_real)
if final_path.exists() and not backup_final.exists():
    shutil.copy2(final_path, backup_final)

# Write the corrected datasets.
real.to_csv(real_path, index=False)
final.to_csv(final_path, index=False)

print("\nAUDIT CORRECTIONS APPLIED SUCCESSFULLY")
print("Audit decisions reviewed:", int(reviewed.sum()))
print("Recorded CHANGE decisions:", len(changes))
print("Categories actually changed:", actual_changed)
print("Real complaints:", len(real))
print("Synthetic complaints:", len(synthetic))
print("Final dataset rows:", len(final))
print("Unique complaint IDs:", final["complaint_id"].nunique())
print("Missing values:", int(final.isna().sum().sum()))
print("Duplicate normalized texts:", int(normalized_text.duplicated().sum()))
print("Real dataset backup:", backup_real.name)
print("Final dataset backup:", backup_final.name)
print("Updated final dataset:", final_path)
