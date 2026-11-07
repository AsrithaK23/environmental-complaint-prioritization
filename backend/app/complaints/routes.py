import logging
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session, joinedload

from backend.app.auth.routes import get_current_user
from backend.app.complaints.schemas import (
    ComplaintListResponse,
    ComplaintResponse,
    ComplaintStatusUpdateRequest,
)
from backend.app.complaints.service import create_complaint
from backend.app.config import settings
from backend.app.database.connection import get_db
from backend.app.database.models import Complaint, User


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/complaints", tags=["Complaints"])


def _can_access_complaint(user: User, complaint: Complaint) -> bool:
    if user.role == "ADMIN":
        return True

    if user.id == complaint.user_id:
        return True

    return (
        user.role == "STAFF"
        and user.department is not None
        and user.department == complaint.assigned_department
    )


def _to_response(complaint: Complaint) -> ComplaintResponse:
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


@router.post(
    "",
    response_model=ComplaintResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_complaint(
    complaint_text: str = Form(..., min_length=10, max_length=2000),
    location: str = Form(..., min_length=2, max_length=100),
    image: UploadFile | None = File(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ComplaintResponse:
    try:
        return create_complaint(
            db=db,
            user=current_user,
            complaint_text=complaint_text,
            location=location,
            image=image,
        )
    finally:
        if image is not None:
            image.file.close()


@router.get("/my", response_model=ComplaintListResponse)
def get_my_complaints(
    status_filter: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ComplaintListResponse:
    query = select(Complaint).where(Complaint.user_id == current_user.id)

    if status_filter is not None:
        allowed_statuses = {
            "Pending",
            "Assigned",
            "In Progress",
            "Resolved",
            "Rejected",
        }
        if status_filter not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid complaint status filter",
            )
        query = query.where(Complaint.status == status_filter)

    total_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(total_query) or 0

    priority_order = case(
        (Complaint.priority == "HIGH", 0),
        (Complaint.priority == "MEDIUM", 1),
        (Complaint.priority == "LOW", 2),
        else_=3,
    )

    complaints = db.scalars(
        query.options(joinedload(Complaint.assigned_staff_user))
        .order_by(
            priority_order,
            Complaint.created_at.asc(),
            Complaint.id.asc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return ComplaintListResponse(
        items=[_to_response(item) for item in complaints],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{complaint_id}/image")
def get_complaint_image(
    complaint_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    complaint = db.get(Complaint, complaint_id)

    if complaint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found",
        )

    if not _can_access_complaint(current_user, complaint):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this complaint",
        )

    if not complaint.image_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This complaint has no image",
        )

    image_path = Path(complaint.image_path)
    if not image_path.is_absolute():
        image_path = Path.cwd() / image_path

    # Ensure the stored path cannot escape the configured upload directory.
    upload_root = Path(settings.upload_dir)
    if not upload_root.is_absolute():
        upload_root = Path.cwd() / upload_root

    try:
        resolved_root = upload_root.resolve()
        resolved_image = image_path.resolve()
        resolved_image.relative_to(resolved_root)
    except (OSError, ValueError):
        logger.error("Stored complaint image path is outside upload directory")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        ) from None

    if not resolved_image.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found",
        )

    suffix = resolved_image.suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }

    return FileResponse(
        path=resolved_image,
        media_type=media_types.get(suffix, "application/octet-stream"),
        filename=resolved_image.name,
        content_disposition_type="inline",
    )


@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(
    complaint_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ComplaintResponse:
    complaint = db.scalar(
        select(Complaint)
        .options(joinedload(Complaint.assigned_staff_user))
        .where(Complaint.id == complaint_id)
    )

    if complaint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found",
        )

    if not _can_access_complaint(current_user, complaint):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this complaint",
        )

    return _to_response(complaint)

# staff endpoints

staff_router = APIRouter(
    prefix="/staff/complaints",
    tags=["Staff"],
)


@staff_router.get("", response_model=ComplaintListResponse)
def get_staff_complaints(
    status_filter: str | None = Query(default=None, alias="status"),
    priority_filter: str | None = Query(default=None, alias="priority"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ComplaintListResponse:
    """List complaints assigned to the current staff member's department."""

    if current_user.role not in {"STAFF", "ADMIN"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff access required",
        )

    if current_user.role == "STAFF" and not current_user.department:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff department is not configured",
        )

    allowed_statuses = {
        "Pending",
        "Assigned",
        "In Progress",
        "Resolved",
        "Rejected",
    }

    allowed_priorities = {"HIGH", "MEDIUM", "LOW"}

    query = select(Complaint)

    # Staff can only see complaints assigned to their department.
    if current_user.role == "STAFF":
        query = query.where(
            Complaint.assigned_department == current_user.department
        )

    if status_filter is not None:
        if status_filter not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid complaint status",
            )

        query = query.where(Complaint.status == status_filter)

    if priority_filter is not None:
        if priority_filter not in allowed_priorities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid complaint priority",
            )

        query = query.where(Complaint.priority == priority_filter)

    total = db.scalar(
        select(func.count()).select_from(query.subquery())
    ) or 0

    complaints = db.scalars(
        query.options(joinedload(Complaint.assigned_staff_user))
        .order_by(
            Complaint.priority.asc(),
            Complaint.created_at.asc(),
            Complaint.id.asc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    # Enum priorities sort alphabetically incorrectly:
    # HIGH, LOW, MEDIUM. Use an explicit ordering instead.
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}

    complaints.sort(
        key=lambda complaint: (
            priority_order.get(complaint.priority, 3),
            complaint.created_at,
            complaint.id,
        )
    )

    return ComplaintListResponse(
        items=[_to_response(complaint) for complaint in complaints],
        total=total,
        page=page,
        page_size=page_size,
    )

@router.patch("/{complaint_id}/status", response_model=ComplaintResponse)
def update_complaint_status(
    complaint_id: int,
    request: ComplaintStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ComplaintResponse:
    """Update complaint status according to the complaint lifecycle."""

    if current_user.role not in {"STAFF", "ADMIN"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff access required",
        )

    complaint = db.scalar(
        select(Complaint)
        .options(joinedload(Complaint.assigned_staff_user))
        .where(Complaint.id == complaint_id)
    )

    if complaint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found",
        )

    # Staff can only update complaints assigned to their department.
    if current_user.role == "STAFF":
        if current_user.department != complaint.assigned_department:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot update complaints assigned to another department",
            )

    allowed_transitions = {
        "Pending": {"Assigned", "Rejected"},
        "Assigned": {"In Progress", "Rejected"},
        "In Progress": {"Resolved", "Rejected"},
        "Resolved": set(),
        "Rejected": set(),
    }

    if request.status not in allowed_transitions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid complaint status",
        )

    if request.status not in allowed_transitions[complaint.status]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot change status from {complaint.status} to {request.status}",
        )

    if request.status in {"Resolved", "Rejected"}:
        if not request.resolution_note or not request.resolution_note.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resolution note is required for Resolved or Rejected complaints",
            )

    if request.status == "Assigned":
        complaint.assigned_staff = current_user.id

    complaint.status = request.status

    if request.resolution_note is not None:
        complaint.resolution_note = request.resolution_note.strip()

    try:
        db.commit()
        db.refresh(complaint)
    except Exception:
        db.rollback()
        raise

    return _to_response(complaint)