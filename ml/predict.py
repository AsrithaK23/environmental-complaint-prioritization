import os
import joblib
import numpy as np

from preprocessing import clean_text


# ============================================================
# MODEL PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "complaint_classifier.pkl"
)

VECTORIZER_PATH = os.path.join(
    BASE_DIR,
    "models",
    "tfidf_vectorizer.pkl"
)


# ============================================================
# LOAD MODEL
# ============================================================

model = joblib.load(
    MODEL_PATH
)

vectorizer = joblib.load(
    VECTORIZER_PATH
)


# ============================================================
# PREDICTION FUNCTION
# ============================================================

def predict_complaint(complaint_text):
    """
    Predict the environmental complaint category.

    Input:
        complaint_text: string

    Output:
        {
            "category": predicted category,
            "confidence": confidence score
        }
    """

    if not complaint_text or not str(complaint_text).strip():
        raise ValueError(
            "Complaint text cannot be empty."
        )

    # Clean complaint
    cleaned_text = clean_text(
        complaint_text
    )

    # Convert text to TF-IDF
    text_vector = vectorizer.transform(
        [cleaned_text]
    )

    # Predict category
    prediction = model.predict(
        text_vector
    )[0]

    # Calculate confidence
    probabilities = model.predict_proba(
        text_vector
    )[0]

    confidence = float(
        np.max(probabilities)
    )

    return {
        "category": str(prediction),
        "confidence": round(
            confidence,
            4
        )
    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print("===================================")
    print("Environmental Complaint Classifier")
    print("===================================")

    complaint = input(
        "\nEnter complaint: "
    )

    try:

        result = predict_complaint(
            complaint
        )

        print("\nPrediction:")
        print(
            "Category:",
            result["category"]
        )

        print(
            "Confidence:",
            result["confidence"]
        )

    except Exception as error:

        print(
            "\nError:",
            error
        )