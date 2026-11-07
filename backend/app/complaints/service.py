import logging
import uuid
from decimal import Decimal
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from backend.app.config import settings
from backend.app.database.models import Complaint, User
from backend.app.complaints.schemas import ComplaintResponse
from backend.app.ml.classifier import classify_complaint
from backend.app.priority.priority_engine import calculate_priority


logger = logging.getLogger(__name__)

CATEGORY_DEPARTMENTS = {
    "Waste Management": "Housekeeping",
    "Water / Sanitation": "Maintenance",
    "Greenery / Landscaping": "Garden / Landscaping",
    "Energy-related Issues": "Electrical / Maintenance",
    "Air Pollution": "Maintenance",
    "Noise Pollution": "Administration",
    "Other": "Administration",
}

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

MAX_TEXT_LENGTH = 2000
MIN_TEXT_LENGTH = 10
MAX_LOCATION_LENGTH = 100
MIN_LOCATION_LENGTH = 2


def _validate_complaint_text(complaint_text: str) -> str:
    text = complaint_text.strip()

    if not MIN_TEXT_LENGTH <= len(text) <= MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Complaint text must contain 10 to 2000 characters.",
        )

    return text


def _validate_location(location: str) -> str:
    cleaned_location = location.strip()

    if not MIN_LOCATION_LENGTH <= len(cleaned_location) <= MAX_LOCATION_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Location must contain 2 to 100 characters.",
        )

    return cleaned_location


def _save_image(upload: UploadFile | None) -> tuple[str | None, Path | None]:
    """
    Validate and save an optional image.

    Returns the stored relative path and absolute path. The absolute path
    is used for cleanup if the database transaction fails.
    """
    if upload is None:
        return None, None

    extension = ALLOWED_IMAGE_TYPES.get(upload.content_type or "")
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Image must be JPEG, PNG, or WEBP.",
        )

    max_bytes = settings.max_image_mb * 1024 * 1024
    upload_dir = Path(settings.upload_dir)
    if not upload_dir.is_absolute():
        upload_dir = Path.cwd() / upload_dir

    try:
        upload.file.seek(0)
        content = upload.file.read(max_bytes + 1)
        upload.file.seek(0)
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not read the uploaded image.",
        ) from exc

    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image must not exceed {settings.max_image_mb} MB.",
        )

    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded image is empty.",
        )

    # Check file signatures rather than trusting only the MIME type.
    valid_signature = (
        extension == ".jpg"
        and content.startswith(b"\xff\xd8\xff")
    ) or (
        extension == ".png"
        and content.startswith(b"\x89PNG\r\n\x1a\n")
    ) or (
        extension == ".webp"
        and len(content) >= 12
        and content.startswith(b"RIFF")
        and content[8:12] == b"WEBP"
    )

    if not valid_signature:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The uploaded file does not match its declared image type.",
        )

    filename = f"{uuid.uuid4().hex}{extension}"
    destination = upload_dir / filename

    try:
        upload_dir.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as image_file:
            image_file.write(content)
    except OSError as exc:
        try:
            destination.unlink(missing_ok=True)
        except OSError:
            logger.exception("Could not remove partially written image")

        logger.exception("Could not store complaint image")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save the uploaded image.",
        ) from exc

    # Store a relative path for portability across development/deployment.
    relative_path = (Path(settings.upload_dir) / filename).as_posix()
    return relative_path, destination


def _build_response(complaint: Complaint) -> ComplaintResponse:
    staff = complaint.assigned_staff_user

    return ComplaintResponse(
        id=complaint.id,
        user_id=complaint.user_id,
        complaint_text=complaint.complaint_text,
        category=complaint.category,
        category_confidence=complaint.category_confidence,
        priority=complaint.priority,
        priority_reason=complaint.priority_reason,
        location=complaint.location,
        has_image=complaint.image_path is not None,
        image_url=(
            f"/api/complaints/{complaint.id}/image"
            if complaint.image_path
            else None
        ),
        assigned_department=complaint.assigned_department,
        assigned_staff=(
            {"id": staff.id, "name": staff.name}
            if staff is not None
            else None
        ),
        status=complaint.status,
        resolution_note=complaint.resolution_note,
        created_at=complaint.created_at,
        updated_at=complaint.updated_at,
    )



def create_complaint(
    db: Session,
    user: User,
    complaint_text: str,
    location: str,
    image: UploadFile | None = None,
) -> ComplaintResponse:
    """Create, classify, prioritize, route, and save a complaint."""
    text = _validate_complaint_text(complaint_text)
    cleaned_location = _validate_location(location)

    image_path: str | None = None
    saved_image: Path | None = None

    try:
        # Validate and save the optional image.
        if image is not None and image.filename:
            image_path, saved_image = _save_image(image)

        # Classify the complaint. ML failure must not block submission.
        try:
            classification = classify_complaint(text)
            category = classification.category
            confidence = classification.confidence
        except Exception:
            logger.exception("Unexpected ML classification failure")
            category = "Other"
            confidence = None

        # Reject invalid categories and confidence values safely.
        if category not in CATEGORY_DEPARTMENTS:
            logger.warning("Invalid ML category; using Other")
            category = "Other"
            confidence = None

        if confidence is not None:
            if (
                isinstance(confidence, bool)
                or not isinstance(confidence, (int, float, Decimal))
                or not 0 <= confidence <= 1
            ):
                logger.warning("Invalid ML confidence; using fallback")
                category = "Other"
                confidence = None

        # Calculate priority and choose the assigned department.
        priority_result = calculate_priority(
            category=category,
            complaint_text=text,
        )

        complaint = Complaint(
            user_id=user.id,
            complaint_text=text,
            category=category,
            category_confidence=(
                Decimal(str(confidence))
                if confidence is not None
                else None
            ),
            priority=priority_result.priority,
            priority_reason=priority_result.reason[:500],
            location=cleaned_location,
            image_path=image_path,
            assigned_department=CATEGORY_DEPARTMENTS[category],
            status="Pending",
        )

        db.add(complaint)
        db.commit()

        # Reload the complaint with its assigned-staff relationship.
        saved_complaint = db.scalar(
            select(Complaint)
            .options(joinedload(Complaint.assigned_staff_user))
            .where(Complaint.id == complaint.id)
        )

        if saved_complaint is None:
            raise RuntimeError("Saved complaint could not be reloaded")

        return _build_response(saved_complaint)

    except Exception:
        db.rollback()

        # Remove the saved image if the database operation fails.
        if saved_image is not None:
            try:
                saved_image.unlink(missing_ok=True)
            except OSError:
                logger.exception("Could not remove orphaned complaint image")

        raise