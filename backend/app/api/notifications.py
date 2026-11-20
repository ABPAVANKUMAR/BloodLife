
from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.notification import Notification
from app.models.user import User

from app.schemas.notification import (
    NotificationResponse,
    NotificationReadResponse
)

from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"]
)


# --------------------------------------------------
# GET MY NOTIFICATIONS
# --------------------------------------------------

@router.get(
    "",
    response_model=list[NotificationResponse]
)
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifications = (
        db.query(Notification)
        .filter(
            Notification.recipient_user_id == current_user.id
        )
        .order_by(Notification.created_at.desc())
        .all()
    )

    return notifications


# --------------------------------------------------
# GET UNREAD NOTIFICATION COUNT
# --------------------------------------------------

@router.get("/unread-count")
def get_unread_notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    count = (
        db.query(Notification)
        .filter(
            Notification.recipient_user_id == current_user.id,
            Notification.is_read.is_(False)
        )
        .count()
    )

    return {
        "unread_count": count
    }


# --------------------------------------------------
# MARK NOTIFICATION AS READ
# --------------------------------------------------

@router.patch(
    "/{notification_id}/read",
    response_model=NotificationReadResponse
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.recipient_user_id == current_user.id
        )
        .first()
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)

        try:
            db.commit()
            db.refresh(notification)

        except Exception:
            db.rollback()
            raise

    return {
        "message": "Notification marked as read",
        "notification": notification
    }
