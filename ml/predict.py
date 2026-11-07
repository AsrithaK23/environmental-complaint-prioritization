
from pathlib import Path
import joblib
import numpy as np

try:
    from .preprocessing import clean_text
except ImportError:
    from preprocessing import clean_text


# ============================================================
# MODEL PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"

MODEL_PATH = MODEL_DIR / "complaint_classifier_candidate.pkl"
VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer_candidate.pkl"


# ============================================================
# LOAD MODEL
# ============================================================

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

if not VECTORIZER_PATH.exists():
    raise FileNotFoundError(
        f"Vectorizer file not found: {VECTORIZER_PATH}"
    )

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


# ============================================================
# PREDICTION FUNCTION
# ============================================================

def predict_complaint(complaint_text):
    """
    Predict an environmental complaint category.

    Returns:
        {
            "category": str,
            "confidence": float,
            "needs_review": bool
        }
    """

    if complaint_text is None or not str(complaint_text).strip():
        raise ValueError("Complaint text cannot be empty.")

    cleaned_text = clean_text(complaint_text)

    if not cleaned_text:
        raise ValueError(
            "Complaint text contains no usable text after cleaning."
        )

    text_vector = vectorizer.transform([cleaned_text])

    prediction = model.predict(text_vector)[0]

    probabilities = model.predict_proba(text_vector)[0]
    confidence = float(np.max(probabilities))

    # Initial review rule, to be validated with real data.
    # This is not a calibrated probability threshold.
    needs_review = confidence < 0.60

    return {
        "category": str(prediction),
        "confidence": round(confidence, 4),
        "needs_review": needs_review,
    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Environmental Complaint Classifier")
    print("=" * 50)

    while True:
        complaint = input(
            "\nEnter complaint (or type 'exit' to quit): "
        ).strip()

        if complaint.lower() == "exit":
            break

        try:
            result = predict_complaint(complaint)

            print("\nPrediction:")
            print("Category:", result["category"])
            print("Confidence:", result["confidence"])
            print("Needs review:", result["needs_review"])

        except ValueError as error:
            print("Input error:", error)
