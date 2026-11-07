from pydantic import BaseModel, Field
from datetime import datetime


class ComplaintAssignmentRequest(BaseModel):
    department: str = Field(min_length=1, max_length=100)
    staff_id: int | None = Field(default=None, gt=0)


class AdminUserResponse(BaseModel):
    id: int
    name: str
    college_id: str
    email: str
    role: str
    department: str | None
    created_at: datetime


class AdminUserListResponse(BaseModel):
    items: list[AdminUserResponse]
    total: int
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)


class AdminUserCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    college_id: str = Field(min_length=1, max_length=50)
    email: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8)
    role: str
    department: str | None = None

class AdminUserUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    role: str | None = None
    department: str | None = None

class AnalyticsTotals(BaseModel):
    total: int
    pending: int
    assigned: int
    in_progress: int
    resolved: int
    rejected: int
    high_priority: int


class AnalyticsBreakdownItem(BaseModel):
    category: str
    count: int


class AnalyticsLocationItem(BaseModel):
    location: str
    count: int


class AnalyticsDepartmentItem(BaseModel):
    department: str
    count: int


class PendingVsResolved(BaseModel):
    pending: int
    resolved: int


class MonthlyTrendItem(BaseModel):
    month: str
    count: int


class AdminAnalyticsResponse(BaseModel):
    totals: AnalyticsTotals
    by_category: list[AnalyticsBreakdownItem]
    by_location: list[AnalyticsLocationItem]
    by_department: list[AnalyticsDepartmentItem]
    pending_vs_resolved: PendingVsResolved
    monthly_trend: list[MonthlyTrendItem]