import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

from preprocessing import clean_text


# ============================================================
# 1. PATHS
# ============================================================

DATASET_PATH = "dataset/complaints_cleaned.csv"

MODEL_DIR = "ml/models"

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "complaint_classifier.pkl"
)

VECTORIZER_PATH = os.path.join(
    MODEL_DIR,
    "tfidf_vectorizer.pkl"
)


# ============================================================
# 2. LOAD DATASET
# ============================================================

print("\nLoading dataset...")

df = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully.")
print("Number of records:", len(df))

print("\nColumns:")
print(df.columns.tolist())


# ============================================================
# 3. CHECK REQUIRED COLUMNS
# ============================================================

required_columns = ["complaint_text", "category"]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(
            f"Required column '{column}' not found in dataset."
        )


# ============================================================
# 4. REMOVE MISSING VALUES
# ============================================================

df = df.dropna(
    subset=["complaint_text", "category"]
).copy()

print("\nRecords after removing missing values:", len(df))


# ============================================================
# 5. CLEAN TEXT
# ============================================================

print("\nCleaning complaint text...")

df["cleaned_text"] = df["complaint_text"].apply(
    clean_text
)


# Remove empty complaints
df = df[df["cleaned_text"].str.len() > 0]

print("Text preprocessing completed.")


# ============================================================
# 6. DISPLAY CATEGORIES
# ============================================================

print("\nComplaint categories:")

print(
    df["category"].value_counts()
)


# ============================================================
# 7. INPUT AND TARGET
# ============================================================

X = df["cleaned_text"]
y = df["category"]


# ============================================================
# 8. TRAIN / TEST SPLIT
# ============================================================

print("\nSplitting dataset...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))


# ============================================================
# 9. TF-IDF
# ============================================================

print("\nCreating TF-IDF features...")

vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),
    stop_words="english"
)

X_train_tfidf = vectorizer.fit_transform(X_train)

X_test_tfidf = vectorizer.transform(X_test)

print(
    "TF-IDF training shape:",
    X_train_tfidf.shape
)


# ============================================================
# 10. TRAIN CLASSIFIER
# ============================================================

print("\nTraining Logistic Regression classifier...")

model = LogisticRegression(
    max_iter=2000
)

model.fit(
    X_train_tfidf,
    y_train
)

print("Model training completed.")


# ============================================================
# 11. PREDICTIONS
# ============================================================

print("\nGenerating predictions...")

y_pred = model.predict(
    X_test_tfidf
)


# ============================================================
# 12. EVALUATION
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("\n========================================")
print("MODEL EVALUATION")
print("========================================")

print(
    f"\nAccuracy: {accuracy:.4f}"
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0
    )
)

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ============================================================
# 13. SAVE MODEL
# ============================================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)

print("\nSaving trained model...")

joblib.dump(
    model,
    MODEL_PATH
)

joblib.dump(
    vectorizer,
    VECTORIZER_PATH
)

print("\n========================================")
print("MODEL SAVED SUCCESSFULLY")
print("========================================")

print(
    f"\nClassifier:\n{MODEL_PATH}"
)

print(
    f"\nTF-IDF Vectorizer:\n{VECTORIZER_PATH}"
)

print("\nTraining process completed.")