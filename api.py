
from time import perf_counter

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ml.predict import predict_complaint

app = FastAPI(
    title="Environmental Complaint NLP API",
    description="AI-based environmental complaint classification",
    version="1.0.0",
)


class ComplaintRequest(BaseModel):
    complaint_text: str = Field(
        ...,
        min_length=1,
        max_length=5000
    )


@app.get("/")
def home():
    return {
        "status": "online",
        "service": "Environmental Complaint NLP API"
    }


@app.post("/predict")
def predict(request: ComplaintRequest):
    complaint = request.complaint_text.strip()

    if not complaint:
        raise HTTPException(
            status_code=422,
            detail="Complaint text cannot be empty."
        )

    start = perf_counter()

    try:
        result = predict_complaint(complaint)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Prediction failed. Check the API server logs."
        )

    elapsed = perf_counter() - start

    if elapsed > 5:
        return {
            "category": "Other",
            "confidence": 0.0,
            "needs_review": True,
            "reason": "Prediction exceeded the 5-second processing limit.",
            "processing_time_seconds": round(elapsed, 3)
        }

    return {
        **result,
        "processing_time_seconds": round(elapsed, 3)
    }