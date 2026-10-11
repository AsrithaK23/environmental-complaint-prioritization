
from pathlib import Path

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

try:
    from .preprocessing import clean_text
except ImportError:
    from preprocessing import clean_text


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = (
    BASE_DIR
    / "dataset"
    / "processed"
    / "complaints_final_for_person2.csv"
)
MODEL_DIR = BASE_DIR / "ml" / "models"

# Candidate filenames preserve existing model artifacts
MODEL_PATH = MODEL_DIR / "complaint_classifier_candidate.pkl"
VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer_candidate.pkl"


def main():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    # 1. Load and validate dataset
    df = pd.read_csv(DATASET_PATH)

    required_columns = {"complaint_text", "category"}
    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"Required columns: {required_columns}. "
            f"Found: {df.columns.tolist()}"
        )

    df = df.dropna(subset=["complaint_text", "category"]).copy()
    df["complaint_text"] = df["complaint_text"].astype(str)
    df["category"] = df["category"].astype(str).str.strip()

    df = df[
        (df["complaint_text"].str.strip() != "")
        & (df["category"] != "")
    ].copy()

    df["cleaned_text"] = df["complaint_text"].apply(clean_text)

    df = df[df["cleaned_text"].str.strip() != ""].copy()

    X = df["cleaned_text"]
    y = df["category"]

    print("=" * 65)
    print("ENVIRONMENTAL COMPLAINT NLP CLASSIFIER")
    print("=" * 65)
    print(f"Usable complaints: {len(df)}")
    print(f"Number of categories: {y.nunique()}")
    print("\nCategory counts:")
    print(y.value_counts().to_string())

    # 2. Stratified 80/20 train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    print(f"\nTraining samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")

    # 3. TF-IDF feature extraction
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        stop_words="english",
        sublinear_tf=True,
    )

    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    print(f"TF-IDF features: {len(vectorizer.get_feature_names_out())}")

    # 4. Train classifier
    model = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42,
    )

    model.fit(X_train_tfidf, y_train)

    # 5. Evaluate on held-out test data
    predictions = model.predict(X_test_tfidf)

    accuracy = accuracy_score(y_test, predictions)

    print("\n" + "=" * 65)
    print("MODEL EVALUATION")
    print("=" * 65)
    print(f"Test accuracy: {accuracy:.4f} ({accuracy * 100:.2f}%)")

    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )

    labels = model.classes_
    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=labels,
    )

    print("Confusion matrix (rows = actual, columns = predicted):")
    print("Labels:", list(labels))
    print(matrix)

    # 6. Save candidate artifacts only after successful evaluation
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    print("\nCandidate artifacts saved successfully:")
    print(MODEL_PATH)
    print(VECTORIZER_PATH)
    print("\nExisting model files were not overwritten.")
    print("Review the evaluation before promoting these candidates.")


if __name__ == "__main__":
    main()
