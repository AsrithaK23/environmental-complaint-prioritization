
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ComplaintResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    complaint_text: str
    category: str
    category_confidence: Decimal | None
    priority: str
    priority_reason: str
    location: str
    has_image: bool
    image_url: str | None
    assigned_department: str
    assigned_staff: dict | None
    status: str
    resolution_note: str | None
    created_at: datetime
    updated_at: datetime


class ComplaintListResponse(BaseModel):
    items: list[ComplaintResponse]
    total: int
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)

class ComplaintStatusUpdateRequest(BaseModel):
    status: str
    resolution_note: str | None = None