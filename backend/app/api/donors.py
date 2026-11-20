
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.donor_profile import DonorProfile
from app.models.user import User

from app.schemas.donor import (
    DonorProfileCreate,
    DonorProfileUpdate,
    DonorProfileResponse,
    AvailabilityUpdate,
    NearbyDonorResponse
)

from app.core.dependencies import get_current_user
from app.services.location_service import calculate_distance_km


router = APIRouter(
    prefix="/api/donors",
    tags=["Donors"]
)


# --------------------------------------------------
# DONOR ROLE VALIDATION
# --------------------------------------------------

def require_donor(user: User):
    if user.role != "donor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only donor accounts can manage donor profiles"
        )


# --------------------------------------------------
# CREATE DONOR PROFILE
# --------------------------------------------------

@router.post(
    "/me",
    response_model=DonorProfileResponse,
    status_code=status.HTTP_201_CREATED
)
def create_donor_profile(
    profile_data: DonorProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_donor(current_user)

    existing_profile = db.query(DonorProfile).filter(
        DonorProfile.user_id == current_user.id
    ).first()

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Donor profile already exists"
        )

    new_profile = DonorProfile(
        user_id=current_user.id,
        **profile_data.model_dump()
    )

    try:
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
    except Exception:
        db.rollback()
        raise

    return new_profile


# --------------------------------------------------
# GET MY DONOR PROFILE
# --------------------------------------------------

@router.get(
    "/me",
    response_model=DonorProfileResponse
)
def get_my_donor_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_donor(current_user)

    profile = db.query(DonorProfile).filter(
        DonorProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor profile not found"
        )

    return profile


# --------------------------------------------------
# UPDATE DONOR PROFILE
# --------------------------------------------------

@router.patch(
    "/me",
    response_model=DonorProfileResponse
)
def update_donor_profile(
    profile_data: DonorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_donor(current_user)

    profile = db.query(DonorProfile).filter(
        DonorProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor profile not found"
        )

    update_data = profile_data.model_dump(
        exclude_unset=True
    )

    for field in ("blood_group", "city"):
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field} cannot be null"
            )

    for field, value in update_data.items():
        setattr(profile, field, value)

    try:
        db.commit()
        db.refresh(profile)
    except Exception:
        db.rollback()
        raise

    return profile


# --------------------------------------------------
# UPDATE DONOR AVAILABILITY
# --------------------------------------------------

@router.patch(
    "/me/availability",
    response_model=DonorProfileResponse
)
def update_donor_availability(
    availability_data: AvailabilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_donor(current_user)

    profile = db.query(DonorProfile).filter(
        DonorProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor profile not found"
        )

    profile.is_available = availability_data.is_available

    try:
        db.commit()
        db.refresh(profile)
    except Exception:
        db.rollback()
        raise

    return profile


# --------------------------------------------------
# NEARBY DONOR DISCOVERY
# --------------------------------------------------

@router.get(
    "/nearby",
    response_model=list[NearbyDonorResponse]
)
def find_nearby_donors(
    city: str = Query(min_length=2, max_length=100),
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
    radius_km: int = Query(default=10),
    blood_group: str | None = Query(default=None),
    locality: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate supported search radius
    if radius_km not in (5, 10, 25, 50):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Radius must be 5, 10, 25 or 50 km"
        )

    # Only discover donors who have opted in
    # and currently marked themselves available.
    query = db.query(DonorProfile).filter(
        DonorProfile.city.ilike(city),
        DonorProfile.is_available.is_(True),
        DonorProfile.discovery_consent.is_(True),
        DonorProfile.latitude.isnot(None),
        DonorProfile.longitude.isnot(None)
    )

    if blood_group:
        query = query.filter(
            DonorProfile.blood_group == blood_group
        )

    if locality:
        query = query.filter(
            DonorProfile.locality.ilike(locality)
        )

    donors = query.all()

    nearby_donors = []

    for donor in donors:
        distance = calculate_distance_km(
            latitude,
            longitude,
            donor.latitude,
            donor.longitude
        )

        if distance <= radius_km:
            nearby_donors.append({
                "id": donor.id,
                "blood_group": donor.blood_group,
                "city": donor.city,
                "locality": donor.locality,
                "is_available": donor.is_available,
                "distance_km": round(distance, 2)
            })

    nearby_donors.sort(
        key=lambda donor: donor["distance_km"]
    )

    return nearby_donors
