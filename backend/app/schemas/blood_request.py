
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------
# COMMON TYPES
# --------------------------------------------------

BloodGroup = Literal[
    "A+", "A-", "B+", "B-",
    "AB+", "AB-", "O+", "O-"
]

Urgency = Literal["critical", "high", "normal"]

RequestStatus = Literal[
    "open", "matched", "fulfilled", "cancelled"
]


# --------------------------------------------------
# CREATE BLOOD REQUEST
# --------------------------------------------------

class BloodRequestCreate(BaseModel):
    blood_group: BloodGroup

    units_required: int = Field(
        default=1,
        ge=1,
        le=20
    )

    hospital_name: str = Field(
        min_length=2,
        max_length=200
    )

    city: str = Field(
        min_length=2,
        max_length=100
    )

    locality: str | None = Field(
        default=None,
        max_length=150
    )

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180
    )

    urgency: Urgency = "high"

    notes: str | None = Field(
        default=None,
        max_length=500
    )


# --------------------------------------------------
# UPDATE REQUEST STATUS
# --------------------------------------------------

class BloodRequestStatusUpdate(BaseModel):
    status: Literal[
        "matched", "fulfilled", "cancelled"
    ]


# --------------------------------------------------
# BLOOD REQUEST RESPONSE
# --------------------------------------------------

class BloodRequestResponse(BaseModel):
    id: int
    requester_id: int
    blood_group: BloodGroup
    units_required: int
    hospital_name: str
    city: str
    locality: str | None
    latitude: float | None
    longitude: float | None
    urgency: Urgency
    status: RequestStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------
# DONOR MATCH RESPONSE
# --------------------------------------------------

class DonorMatchResponse(BaseModel):
    donor_id: int
    blood_group: BloodGroup
    city: str
    locality: str | None
    distance_km: float
