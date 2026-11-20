
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User
from app.models.donor_profile import DonorProfile
from app.models.blood_request import BloodRequest


def create_blood_match_notification(
    db: Session,
    donor_id: int,
    blood_request: BloodRequest
) -> bool:

    donor = db.query(DonorProfile).filter(
        DonorProfile.id == donor_id
    ).first()

    if donor is None:
        return False

    user = db.query(User).filter(
        User.id == donor.user_id,
        User.is_active.is_(True)
    ).first()

    if user is None:
        return False

    existing = db.query(Notification).filter(
        Notification.request_id == blood_request.id,
        Notification.recipient_user_id == user.id,
        Notification.notification_type == "blood_request_match"
    ).first()

    if existing:
        return False

    notification = Notification(
        recipient_user_id=user.id,
        request_id=blood_request.id,
        notification_type="blood_request_match",
        title="Emergency Blood Request",
        message=(
            f"A nearby emergency blood request needs "
            f"{blood_request.blood_group} blood. "
            f"Hospital: {blood_request.hospital_name}. "
            f"Location: {blood_request.city}."
        ),
        is_read=False
    )

    db.add(notification)

    return True
