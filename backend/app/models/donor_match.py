
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint
)

from app.db.database import Base


class DonorMatch(Base):
    __tablename__ = "donor_matches"

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'accepted', 'declined', 'expired')",
            name="check_donor_match_status"
        ),
        CheckConstraint(
            "distance_km >= 0",
            name="check_donor_match_distance"
        ),
        UniqueConstraint(
            "request_id",
            "donor_id",
            name="unique_request_donor_match"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    request_id = Column(
        Integer,
        ForeignKey("blood_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    donor_id = Column(
        Integer,
        ForeignKey("donor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    distance_km = Column(Float, nullable=False)

    status = Column(
        String(20),
        nullable=False,
        default="pending",
        index=True
    )

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
