
import logging
import time
from dataclasses import dataclass

import httpx

from backend.app.config import settings


logger = logging.getLogger(__name__)

VALID_CATEGORIES = {
    "Waste Management",
    "Water / Sanitation",
    "Air Pollution",
    "Noise Pollution",
    "Energy-related Issues",
    "Greenery / Landscaping",
    "Other",
}


@dataclass(frozen=True)
class ClassificationResult:
    category: str
    confidence: float | None


def _fallback() -> ClassificationResult:
    return ClassificationResult(category="Other", confidence=None)


def classify_complaint(text: str) -> ClassificationResult:
    """
    Classify raw complaint text using the ML service.

    Retries once after a timeout or server error.
    Falls back to Other/None if the service is unavailable or
    returns an invalid response.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Complaint text must not be empty")

    # The development stub avoids depending on Person 2's service.
    if settings.ml_use_stub:
        logger.info("ML stub enabled; returning fallback category")
        return _fallback()

    base_url = settings.ml_service_url.rstrip("/")
    endpoint = f"{base_url}/predict"
    timeout = settings.ml_timeout_seconds

    for attempt in range(2):
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(
                    endpoint,
                    json={"complaint_text": text},
                )

            # Retry only server-side errors once.
            if response.status_code >= 500:
                logger.warning(
                    "ML service returned HTTP %s (attempt %s/2)",
                    response.status_code,
                    attempt + 1,
                )
                if attempt == 0:
                    time.sleep(0.2)
                    continue
                return _fallback()

            # Client errors are not retryable.
            response.raise_for_status()

            try:
                payload = response.json()
            except ValueError:
                logger.warning("ML service returned invalid JSON")
                return _fallback()

            if not isinstance(payload, dict):
                logger.warning("ML service response was not a JSON object")
                return _fallback()

            category = payload.get("category")
            confidence = payload.get("confidence")

            if not isinstance(category, str) or category not in VALID_CATEGORIES:
                logger.warning("ML service returned an invalid category")
                return _fallback()

            if confidence is not None:
                # bool is a subclass of int in Python; reject it explicitly.
                if (
                    isinstance(confidence, bool)
                    or not isinstance(confidence, (int, float))
                    or not 0.0 <= confidence <= 1.0
                ):
                    logger.warning("ML service returned invalid confidence")
                    return _fallback()

                confidence = float(confidence)

            return ClassificationResult(
                category=category,
                confidence=confidence,
            )

        except (httpx.TimeoutException, httpx.TransportError) as exc:
            logger.warning(
                "ML service connection failed (attempt %s/2): %s",
                attempt + 1,
                type(exc).__name__,
            )
            if attempt == 0:
                time.sleep(0.2)
                continue
            return _fallback()

        except httpx.HTTPStatusError as exc:
            logger.warning(
                "ML service returned non-retryable HTTP status %s",
                exc.response.status_code,
            )
            return _fallback()

    return _fallback()