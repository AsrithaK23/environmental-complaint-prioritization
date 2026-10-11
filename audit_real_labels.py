
import pandas as pd
import re
from pathlib import Path

INPUT = Path("dataset/processed/complaints_cleaned.csv")
OUTPUT = Path("dataset/processed/real_label_audit_review.csv")

if not INPUT.exists():
    raise FileNotFoundError(
        f"Dataset not found: {INPUT.resolve()}\n"
        "Run this script from the ESP-Project root folder."
    )

df = pd.read_csv(INPUT)

required = {"complaint_id", "complaint_text", "category"}
if not required.issubset(df.columns):
    raise ValueError(f"Missing columns: {required - set(df.columns)}")

# These rules only flag possible mistakes for human review.
# They do NOT automatically change any original category.
rules = [
    (
        "Water / Sanitation",
        r"\b(sewage|sewer|septic|drainage|blocked drain|"
        r"drain blocked|wastewater|waste water|waterlogging|"
        r"water logging|stagnant water|overflowing drain|"
        r"water leakage|water leak|burst pipe)\b"
    ),
    (
        "Energy-related Issues",
        r"\b(street ?lights?|streetlamp|power cut|power outage|"
        r"electricity outage|no electricity|exposed wire|"
        r"live wire|short circuit|electrical fault|"
        r"transformer|broken electrical cable)\b"
    ),
    (
        "Air Pollution",
        r"\b(smoke|fumes|exhaust|dust pollution|dusty air|"
        r"burning garbage|burning rubbish|burning waste|"
        r"burning leaves|chemical smell|diesel smell)\b"
    ),
    (
        "Noise Pollution",
        r"\b(noise pollution|loud music|loudspeaker|"
        r"loud honking|constant honking|excessive noise|"
        r"disturbing noise|very noisy|too noisy)\b"
    ),
    (
        "Greenery / Landscaping",
        r"\b(drying plants|drying tree|dead plants|"
        r"overgrown grass|overgrown weeds|tree branches|"
        r"broken tree branch|damaged saplings|"
        r"plants need watering|garden maintenance)\b"
    ),
    (
        "Waste Management",
        r"\b(garbage|rubbish|litter|overflowing bin|"
        r"overflowing dustbin|waste collection|"
        r"dumped waste|trash|uncollected waste)\b"
    ),
]

def suggested_category(text):
    text = str(text).lower()
    matches = [
        category for category, pattern in rules
        if re.search(pattern, text)
    ]
    # Multiple category clues are ambiguous; leave them for manual review.
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        return "MANUAL REVIEW - MULTIPLE CLUES"
    return ""

df["complaint_text"] = df["complaint_text"].fillna("").astype(str)
df["category"] = df["category"].fillna("").astype(str).str.strip()

df["suggested_category"] = df["complaint_text"].apply(
    suggested_category
)

df["review_reason"] = df.apply(
    lambda row: (
        "Possible category mismatch"
        if row["suggested_category"]
        and row["suggested_category"] != row["category"]
        and not row["suggested_category"].startswith("MANUAL REVIEW")
        else (
            "Multiple category clues - check manually"
            if row["suggested_category"].startswith("MANUAL REVIEW")
            else ""
        )
    ),
    axis=1
)

review = df[df["review_reason"] != ""].copy()
review["manual_decision"] = ""
review["corrected_category"] = ""

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
review.to_csv(OUTPUT, index=False, encoding="utf-8")

print("Real dataset rows:", len(df))
print("Rows flagged for review:", len(review))
print("Original dataset was NOT modified.")
print("Review file saved to:", OUTPUT.resolve())

if len(review):
    print("\nReview candidates by current category:")
    print(review["category"].value_counts().to_string())
    print("\nOpen the CSV and inspect complaint_text, category,")
    print("suggested_category, and review_reason.")
