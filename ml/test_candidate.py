
from pathlib import Path
import joblib

try:
    from .preprocessing import clean_text
except ImportError:
    from preprocessing import clean_text

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"

model = joblib.load(
    MODEL_DIR / "complaint_classifier_candidate.pkl"
)
vectorizer = joblib.load(
    MODEL_DIR / "tfidf_vectorizer_candidate.pkl"
)

test_complaints = [
    "Garbage has not been collected near the hostel for three days.",
    "There is no drinking water supply in the college building.",
    "Smoke from burning plastic is affecting students.",
    "Loud construction noise is disturbing classes.",
    "The streetlights are not working near the parking area.",
    "The garden plants are dying because nobody waters them.",
    "There is an environmental problem that needs investigation.",
]

print("=" * 60)
print("CANDIDATE MODEL PREDICTION TEST")
print("=" * 60)

for i, complaint in enumerate(test_complaints, start=1):
    cleaned = clean_text(complaint)
    features = vectorizer.transform([cleaned])
    prediction = model.predict(features)[0]

    print(f"\nTest {i}")
    print("Complaint :", complaint)
    print("Prediction:", prediction)
