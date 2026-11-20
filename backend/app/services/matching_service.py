
from sqlalchemy.orm import Session

from app.models.donor_profile import DonorProfile
from app.models.blood_request import BloodRequest
from app.services.location_service import calculate_distance_km


# Red blood cell (RBC) compatibility reference.
# This is for coordination support, not clinical approval.

RBC_COMPATIBILITY = {
    "A+": ["A+", "A-", "O+", "O-"],
    "A-": ["A-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
    "AB-": ["A-", "B-", "AB-", "O-"],
    "O+": ["O+", "O-"],
    "O-": ["O-"]
}


def find_compatible_donors(
    db: Session,
    blood_request: BloodRequest,
    radius_km: int = 10
) -> list[dict]:

    if radius_km not in (5, 10, 25, 50):
        raise ValueError(
            "Radius must be 5, 10, 25 or 50 km"
        )

    if (
        blood_request.latitude is None
        or blood_request.longitude is None
    ):
        raise ValueError(
            "Request must have both latitude and longitude"
        )

    compatible_groups = RBC_COMPATIBILITY.get(
        blood_request.blood_group
    )

    if not compatible_groups:
        return []

    # Find available donors who have consented
    # to appear in donor discovery.
    donors = (
        db.query(DonorProfile)
        .filter(
            DonorProfile.city.ilike(blood_request.city),
            DonorProfile.blood_group.in_(compatible_groups),
            DonorProfile.is_available.is_(True),
            DonorProfile.discovery_consent.is_(True),
            DonorProfile.latitude.isnot(None),
            DonorProfile.longitude.isnot(None)
        )
        .all()
    )

    matches = []

    for donor in donors:

        distance = calculate_distance_km(
            blood_request.latitude,
            blood_request.longitude,
            donor.latitude,
            donor.longitude
        )

        if distance <= radius_km:
            matches.append({
                "donor_id": donor.id,
                "blood_group": donor.blood_group,
                "city": donor.city,
                "locality": donor.locality,
                "distance_km": distance
            })

    # Nearest donors appear first
    matches.sort(
        key=lambda donor: donor["distance_km"]
    )

    return matches
