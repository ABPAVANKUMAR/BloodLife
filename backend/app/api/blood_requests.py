
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.blood_request import BloodRequest
from app.models.user import User
from app.models.donor_match import DonorMatch

from app.schemas.blood_request import (
    BloodRequestCreate,
    BloodRequestResponse,
    BloodRequestStatusUpdate,
    DonorMatchResponse
)

from app.core.dependencies import get_current_user

from app.services.matching_service import (
    find_compatible_donors
)


router = APIRouter(
    prefix="/api/requests",
    tags=["Emergency Blood Requests"]
)


# --------------------------------------------------
# CREATE EMERGENCY BLOOD REQUEST
# --------------------------------------------------

@router.post(
    "",
    response_model=BloodRequestResponse,
    status_code=status.HTTP_201_CREATED
)
def create_blood_request(
    request_data: BloodRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "requester":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only requester accounts can create blood requests"
        )

    if (
        (request_data.latitude is None)
        != (request_data.longitude is None)
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Latitude and longitude must both be provided or both be omitted"
        )

    new_request = BloodRequest(
        requester_id=current_user.id,
        **request_data.model_dump()
    )

    try:
        db.add(new_request)
        db.commit()
        db.refresh(new_request)

    except Exception:
        db.rollback()
        raise

    return new_request


# --------------------------------------------------
# GET MY BLOOD REQUESTS
# --------------------------------------------------

@router.get(
    "/my",
    response_model=list[BloodRequestResponse]
)
def get_my_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    requests = (
        db.query(BloodRequest)
        .filter(
            BloodRequest.requester_id == current_user.id
        )
        .order_by(BloodRequest.created_at.desc())
        .all()
    )

    return requests


# --------------------------------------------------
# GET ALL OPEN BLOOD REQUESTS
# --------------------------------------------------

@router.get(
    "",
    response_model=list[BloodRequestResponse]
)
def get_open_requests(
    city: str | None = Query(
        default=None,
        min_length=2,
        max_length=100
    ),
    blood_group: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(BloodRequest).filter(
        BloodRequest.status == "open"
    )

    if city:
        query = query.filter(
            BloodRequest.city.ilike(city)
        )

    if blood_group:
        valid_groups = (
            "A+", "A-", "B+", "B-",
            "AB+", "AB-", "O+", "O-"
        )

        if blood_group not in valid_groups:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid blood group"
            )

        query = query.filter(
            BloodRequest.blood_group == blood_group
        )

    return query.order_by(
        BloodRequest.created_at.desc()
    ).all()


# --------------------------------------------------
# GET BLOOD REQUEST BY ID
# --------------------------------------------------

@router.get(
    "/{request_id}",
    response_model=BloodRequestResponse
)
def get_request_by_id(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    blood_request = db.query(BloodRequest).filter(
        BloodRequest.id == request_id
    ).first()

    if not blood_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood request not found"
        )

    if (
        blood_request.requester_id != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot view another user's request"
        )

    return blood_request


# --------------------------------------------------
# FIND AND SAVE COMPATIBLE NEARBY DONORS
# --------------------------------------------------

@router.get(
    "/{request_id}/matches",
    response_model=list[DonorMatchResponse]
)
def get_request_matches(
    request_id: int,
    radius_km: int = Query(default=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    blood_request = db.query(BloodRequest).filter(
        BloodRequest.id == request_id
    ).first()

    if not blood_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood request not found"
        )

    if (
        blood_request.requester_id != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot view matches for another user's request"
        )

    if blood_request.status not in ("open", "matched"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Matching is unavailable for closed requests"
        )

    try:
        matches = find_compatible_donors(
            db=db,
            blood_request=blood_request,
            radius_km=radius_km
        )

        for match in matches:

            existing_match = db.query(DonorMatch).filter(
                DonorMatch.request_id == request_id,
                DonorMatch.donor_id == match["donor_id"]
            ).first()

            if existing_match:
                # Update distance but preserve donor response status.
                existing_match.distance_km = match["distance_km"]

            else:
                new_match = DonorMatch(
                    request_id=request_id,
                    donor_id=match["donor_id"],
                    distance_km=match["distance_km"],
                    status="pending"
                )

                db.add(new_match)

        db.commit()

        return matches

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error)
        )

    except Exception:
        db.rollback()
        raise


# --------------------------------------------------
# UPDATE BLOOD REQUEST STATUS
# --------------------------------------------------

@router.patch(
    "/{request_id}/status",
    response_model=BloodRequestResponse
)
def update_request_status(
    request_id: int,
    status_data: BloodRequestStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    blood_request = db.query(BloodRequest).filter(
        BloodRequest.id == request_id
    ).first()

    if not blood_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood request not found"
        )

    if (
        blood_request.requester_id != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot update another user's request"
        )

    if blood_request.status in ("fulfilled", "cancelled"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This request is already closed"
        )

    blood_request.status = status_data.status

    try:
        db.commit()
        db.refresh(blood_request)

    except Exception:
        db.rollback()
        raise

    return blood_request
