
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from backend.app.auth.routes import get_current_user
from backend.app.complaints.routes import _to_response
from backend.app.complaints.schemas import ComplaintResponse
from backend.app.database.connection import get_db
from backend.app.database.models import Complaint, User
from backend.app.admin.schemas import ComplaintAssignmentRequest

from sqlalchemy import func
from backend.app.complaints.schemas import ComplaintListResponse
from backend.app.admin.schemas import (
    AdminUserCreateRequest,
    AdminUserListResponse,
    AdminUserResponse,
    AdminUserUpdateRequest,
    AdminAnalyticsResponse,
)
from backend.app.auth.security import hash_password


router = APIRouter(
    prefix="/admin/complaints",
    tags=["Admin"],
)

users_router = APIRouter(
    prefix="/admin/users",
    tags=["Admin"],
)

analytics_router = APIRouter(
    prefix="/admin/analytics",
    tags=["Admin"],
)


VALID_DEPARTMENTS = {
    "Housekeeping",
    "Maintenance",
    "Garden / Landscaping",
    "Electrical / Maintenance",
    "Administration",
}


@router.patch("/{complaint_id}/assign", response_model=ComplaintResponse)
def assign_complaint(
    complaint_id: int,
    request: ComplaintAssignmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Only admins can assign complaints.
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    # Validate department.
    if request.department not in VALID_DEPARTMENTS:
        raise HTTPException(
            status_code=400,
            detail="Invalid department",
        )

    # Find complaint.
    complaint = db.scalar(
        select(Complaint)
        .options(joinedload(Complaint.assigned_staff_user))
        .where(Complaint.id == complaint_id)
    )

    if complaint is None:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found",
        )

    # If a staff member is provided, verify their role and department.
    if request.staff_id is not None:
        staff = db.scalar(
            select(User).where(User.id == request.staff_id)
        )

        if staff is None or staff.role != "STAFF":
            raise HTTPException(
                status_code=400,
                detail="Invalid staff member",
            )

        if staff.department != request.department:
            raise HTTPException(
                status_code=400,
                detail="Staff member does not belong to the selected department",
            )

    # Update assignment.
    complaint.assigned_department = request.department
    complaint.assigned_staff = request.staff_id

    try:
        db.commit()
        db.refresh(complaint)
    except Exception:
        db.rollback()
        raise

    # Reload staff relationship for the response.
    db.refresh(complaint)

    return _to_response(complaint)


@router.get("", response_model=ComplaintListResponse)
def get_admin_complaints(
    status: str | None = None,
    priority: str | None = None,
    category: str | None = None,
    department: str | None = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    if page < 1 or page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=400,
            detail="Invalid pagination values",
        )

    filters = []

    if status:
        filters.append(Complaint.status == status)

    if priority:
        filters.append(Complaint.priority == priority)

    if category:
        filters.append(Complaint.category == category)

    if department:
        filters.append(Complaint.assigned_department == department)

    total = db.scalar(
        select(func.count(Complaint.id)).where(*filters)
    ) or 0

    complaints = db.scalars(
        select(Complaint)
        .options(joinedload(Complaint.assigned_staff_user))
        .where(*filters)
        .order_by(Complaint.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return ComplaintListResponse(
        items=[_to_response(complaint) for complaint in complaints],
        total=total,
        page=page,
        page_size=page_size,
    )


@users_router.get("", response_model=AdminUserListResponse)
def get_admin_users(
    role: str | None = None,
    department: str | None = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    if page < 1 or page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=400,
            detail="Invalid pagination values",
        )

    filters = []

    if role:
        filters.append(User.role == role)

    if department:
        filters.append(User.department == department)

    total = db.scalar(
        select(func.count(User.id)).where(*filters)
    ) or 0

    users = db.scalars(
        select(User)
        .where(*filters)
        .order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return AdminUserListResponse(
        items=[
            AdminUserResponse(
                id=user.id,
                name=user.name,
                college_id=user.college_id,
                email=user.email,
                role=user.role,
                department=user.department,
                created_at=user.created_at,
            )
            for user in users
        ],
        total=total,
        page=page,
        page_size=page_size,
    )

@users_router.post("", response_model=AdminUserResponse, status_code=201)
def create_admin_user(
    request: AdminUserCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    if request.role not in ["STAFF", "ADMIN"]:
        raise HTTPException(
            status_code=400,
            detail="Role must be STAFF or ADMIN",
        )

    allowed_departments = [
        "Housekeeping",
        "Maintenance",
        "Garden / Landscaping",
        "Electrical / Maintenance",
        "Administration",
    ]

    if request.role == "STAFF":
        if request.department not in allowed_departments:
            raise HTTPException(
                status_code=400,
                detail="Valid department is required for STAFF",
            )
    else:
        request.department = None

    existing_user = db.scalar(
        select(User).where(
            (User.email == request.email)
            | (User.college_id == request.college_id)
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email or college ID already exists",
        )

    new_user = User(
        name=request.name,
        college_id=request.college_id,
        email=request.email,
        password_hash=hash_password(request.password),
        role=request.role,
        department=request.department,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return AdminUserResponse(
        id=new_user.id,
        name=new_user.name,
        college_id=new_user.college_id,
        email=new_user.email,
        role=new_user.role,
        department=new_user.department,
        created_at=new_user.created_at,
    )

@users_router.patch("/{user_id}", response_model=AdminUserResponse)
def update_admin_user(
    user_id: int,
    request: AdminUserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if request.role is not None:
        if request.role not in ["USER", "STAFF", "ADMIN"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid role",
            )
        user.role = request.role

    if request.name is not None:
        user.name = request.name

    if request.department is not None:
        allowed_departments = [
            "Housekeeping",
            "Maintenance",
            "Garden / Landscaping",
            "Electrical / Maintenance",
            "Administration",
        ]

        if request.department not in allowed_departments:
            raise HTTPException(
                status_code=400,
                detail="Invalid department",
            )

        user.department = request.department

    if user.role == "STAFF" and not user.department:
        raise HTTPException(
            status_code=400,
            detail="STAFF must have a department",
        )

    if user.role != "STAFF":
        user.department = None

    db.commit()
    db.refresh(user)

    return AdminUserResponse(
        id=user.id,
        name=user.name,
        college_id=user.college_id,
        email=user.email,
        role=user.role,
        department=user.department,
        created_at=user.created_at,
    )

@analytics_router.get("", response_model=AdminAnalyticsResponse)
def get_admin_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    complaints = db.query(Complaint).all()

    total = len(complaints)

    pending = sum(c.status == "Pending" for c in complaints)
    assigned = sum(c.status == "Assigned" for c in complaints)
    in_progress = sum(c.status == "In Progress" for c in complaints)
    resolved = sum(c.status == "Resolved" for c in complaints)
    rejected = sum(c.status == "Rejected" for c in complaints)

    high_priority = sum(
        c.priority == "HIGH"
        and c.status not in ["Resolved", "Rejected"]
        for c in complaints
    )

    by_category = {}
    by_location = {}
    by_department = {}
    monthly_trend = {}

    for c in complaints:
        by_category[c.category] = by_category.get(c.category, 0) + 1
        by_location[c.location] = by_location.get(c.location, 0) + 1

        if c.assigned_department:
            by_department[c.assigned_department] = (
                by_department.get(c.assigned_department, 0) + 1
            )

        if c.created_at:
            month = c.created_at.strftime("%Y-%m")
            monthly_trend[month] = monthly_trend.get(month, 0) + 1

    return AdminAnalyticsResponse(
        totals={
            "total": total,
            "pending": pending,
            "assigned": assigned,
            "in_progress": in_progress,
            "resolved": resolved,
            "rejected": rejected,
            "high_priority": high_priority,
        },
        by_category=[
            {"category": k, "count": v}
            for k, v in sorted(by_category.items())
        ],
        by_location=[
            {"location": k, "count": v}
            for k, v in sorted(by_location.items())
        ],
        by_department=[
            {"department": k, "count": v}
            for k, v in sorted(by_department.items())
        ],
        pending_vs_resolved={
            "pending": pending,
            "resolved": resolved,
        },
        monthly_trend=[
            {"month": k, "count": v}
            for k, v in sorted(monthly_trend.items())
        ],
    )