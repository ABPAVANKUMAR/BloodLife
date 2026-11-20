
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
    ForeignKey,
    CheckConstraint
)

from app.db.database import Base


class BloodRequest(Base):
    __tablename__ = "blood_requests"

    __table_args__ = (
        CheckConstraint(
            "blood_group IN ('A+', 'A-', 'B+', 'B-', "
            "'AB+', 'AB-', 'O+', 'O-')",
            name="check_request_blood_group"
        ),
        CheckConstraint(
            "units_required > 0",
            name="check_request_units"
        ),
        CheckConstraint(
            "urgency IN ('critical', 'high', 'normal')",
            name="check_request_urgency"
        ),
        CheckConstraint(
            "status IN ('open', 'matched', 'fulfilled', 'cancelled')",
            name="check_request_status"
        ),
        CheckConstraint(
            "(latitude IS NULL AND longitude IS NULL) OR "
            "(latitude IS NOT NULL AND longitude IS NOT NULL)",
            name="check_request_coordinates_pair"
        ),
        CheckConstraint(
            "latitude IS NULL OR (latitude >= -90 AND latitude <= 90)",
            name="check_request_latitude"
        ),
        CheckConstraint(
            "longitude IS NULL OR (longitude >= -180 AND longitude <= 180)",
            name="check_request_longitude"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    requester_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    blood_group = Column(String(3), nullable=False, index=True)

    units_required = Column(Integer, nullable=False, default=1)

    hospital_name = Column(String(200), nullable=False)

    city = Column(String(100), nullable=False, index=True)

    locality = Column(String(150), nullable=True)

    latitude = Column(Float, nullable=True)

    longitude = Column(Float, nullable=True)

    urgency = Column(
        String(20),
        nullable=False,
        default="high"
    )

    status = Column(
        String(20),
        nullable=False,
        default="open",
        index=True
    )

    notes = Column(String(500), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
