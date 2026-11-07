from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    TIMESTAMP,
    text,
)
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.connection import Base

UnsignedBigInt = BigInteger().with_variant(BIGINT(unsigned=True), "mysql")

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        UnsignedBigInt, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    college_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    role: Mapped[str] = mapped_column(
        Enum("USER", "STAFF", "ADMIN", name="user_role"),
        nullable=False,
        server_default=text("'USER'"),
    )
    department: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    submitted_complaints: Mapped[list["Complaint"]] = relationship(
        back_populates="user",
        foreign_keys="Complaint.user_id",
    )
    assigned_complaints: Mapped[list["Complaint"]] = relationship(
        back_populates="assigned_staff_user",
        foreign_keys="Complaint.assigned_staff",
    )


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(
        UnsignedBigInt, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        UnsignedBigInt,
        ForeignKey("users.id"),
        nullable=False,
    )
    complaint_text: Mapped[str] = mapped_column(
        String(2000), nullable=False
    )
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        server_default=text("'Other'"),
    )
    category_confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    priority: Mapped[str] = mapped_column(
        Enum("HIGH", "MEDIUM", "LOW", name="complaint_priority"),
        nullable=False,
        server_default=text("'MEDIUM'"),
    )
    priority_reason: Mapped[str] = mapped_column(
        String(500), nullable=False
    )
    location: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    image_path: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    assigned_department: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    assigned_staff: Mapped[int | None] = mapped_column(
        UnsignedBigInt,
        ForeignKey("users.id"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        Enum(
            "Pending",
            "Assigned",
            "In Progress",
            "Resolved",
            "Rejected",
            name="complaint_status",
        ),
        nullable=False,
        server_default=text("'Pending'"),
    )
    resolution_note: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )

    user: Mapped["User"] = relationship(
        back_populates="submitted_complaints",
        foreign_keys=[user_id],
    )
    assigned_staff_user: Mapped["User | None"] = relationship(
        back_populates="assigned_complaints",
        foreign_keys=[assigned_staff],
    )

    __table_args__ = (
        Index("idx_complaints_user_created", "user_id", "created_at"),
        Index(
            "idx_complaints_department_status",
            "assigned_department",
            "status",
        ),
        Index("idx_complaints_priority_created", "priority", "created_at"),
        Index("idx_complaints_category", "category"),
        Index("idx_complaints_location", "location"),
    )
