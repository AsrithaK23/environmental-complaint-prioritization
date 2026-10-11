# Environmental Complaint Dataset

## 1. Purpose

This dataset was prepared for the Environmental Complaint Prioritization System. It provides labelled campus-related complaints for training and evaluating an NLP-based complaint classification model.

The NLP model is intended to predict the **complaint category**. Complaint classification and complaint priority prediction are separate tasks.

## 2. Complaint Categories

The dataset contains seven categories:

1. Waste Management
2. Water / Sanitation
3. Air Pollution
4. Noise Pollution
5. Energy-related Issues
6. Greenery / Landscaping
7. Other

Refer to `docs/category_definitions.md` for the detailed definitions of these categories.

## 3. Dataset Structure

- `dataset/raw/` — Source and supplementary datasets.
- `dataset/processed/complaints_cleaned.csv` — Cleaned real complaint dataset.
- `dataset/processed/real_label_audit_review.csv` — Label audit decisions and proposed corrections.
- `dataset/processed/complaints_final_for_person2.csv` — Final combined dataset for NLP classification.

## 4. Final Dataset Details

The final dataset contains **10,365 complaint records**:

- Real complaints: 6,979
- Synthetic complaints: 3,386

The real and synthetic records are combined in `complaints_final_for_person2.csv`.

## 5. Data Preprocessing and Label Audit

The dataset preparation process included:

- Removing unusable or irrelevant complaint records.
- Checking for missing values and duplicate complaint IDs.
- Checking for duplicate complaint texts after lowercase and whitespace normalization.
- Reviewing potentially incorrect or ambiguous category labels.
- Applying the recorded category corrections to the cleaned real dataset.
- Combining the cleaned real complaints with the synthetic supplement.

A total of 245 flagged complaints were reviewed: 200 complaints with multiple category clues and 45 possible category mismatches. The review recorded 100 CHANGE decisions, resulting in 99 actual category changes.

## 6. CSV Columns

| Column | Description |
|---|---|
| `complaint_id` | Unique identifier for a complaint |
| `complaint_text` | Text describing the complaint |
| `category` | Assigned complaint category used as the classification label |
| `source_type` | Indicates whether the record is real or synthetic |

## 7. Instructions for NLP Model Development

Use `dataset/processed/complaints_final_for_person2.csv` as the input dataset for complaint category classification.

- Use `complaint_text` as the input feature.
- Use `category` as the target label.
- Do not use `complaint_id` or `source_type` as predictive text features.
- Split the dataset into training, validation, and test sets before model evaluation.
- Ensure that duplicate or closely related complaints do not leak across the training and test sets.
- Evaluate performance across all seven categories.

**Note:** Synthetic records should be identified separately during evaluation. Report performance on a held-out real-complaint test set separately where possible, to assess how well the model generalizes to real complaints.