
from datetime import date, datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    CheckConstraint
)

from app.db.database import Base


class DonorProfile(Base):
    __tablename__ = "donor_profiles"

    __table_args__ = (
        CheckConstraint(
            "blood_group IN ('A+', 'A-', 'B+', 'B-', "
            "'AB+', 'AB-', 'O+', 'O-')",
            name="check_donor_blood_group"
        ),
        CheckConstraint(
            "latitude IS NULL OR (latitude >= -90 AND latitude <= 90)",
            name="check_donor_latitude"
        ),
        CheckConstraint(
            "longitude IS NULL OR (longitude >= -180 AND longitude <= 180)",
            name="check_donor_longitude"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )

    blood_group = Column(String(3), nullable=False, index=True)

    phone = Column(String(20), nullable=True)

    city = Column(String(100), nullable=False, index=True)

    locality = Column(String(150), nullable=True)

    latitude = Column(Float, nullable=True)

    longitude = Column(Float, nullable=True)

    is_available = Column(
        Boolean,
        default=True,
        nullable=False
    )

    discovery_consent = Column(
        Boolean,
        default=False,
        nullable=False
    )

    last_donation_date = Column(Date, nullable=True)

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
