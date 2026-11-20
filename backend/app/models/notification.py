
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint
)

from app.db.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    __table_args__ = (
        UniqueConstraint(
            "request_id",
            "recipient_user_id",
            "notification_type",
            name="uq_request_recipient_notification"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    recipient_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    request_id = Column(
        Integer,
        ForeignKey("blood_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    notification_type = Column(
        String(50),
        nullable=False,
        default="blood_request_match"
    )

    title = Column(
        String(200),
        nullable=False
    )

    message = Column(
        Text,
        nullable=False
    )

    is_read = Column(
        Boolean,
        nullable=False,
        default=False
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    read_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
