
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


BloodGroup = Literal[
    "A+", "A-", "B+", "B-",
    "AB+", "AB-", "O+", "O-"
]


class DonorProfileCreate(BaseModel):
    blood_group: BloodGroup
    phone: str | None = Field(default=None, max_length=20)
    city: str = Field(min_length=2, max_length=100)
    locality: str | None = Field(default=None, max_length=150)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    discovery_consent: bool = False
    last_donation_date: date | None = None


class DonorProfileUpdate(BaseModel):
    blood_group: BloodGroup | None = None
    phone: str | None = Field(default=None, max_length=20)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    locality: str | None = Field(default=None, max_length=150)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    discovery_consent: bool | None = None
    last_donation_date: date | None = None


class AvailabilityUpdate(BaseModel):
    is_available: bool


class DonorProfileResponse(BaseModel):
    id: int
    user_id: int
    blood_group: BloodGroup
    phone: str | None
    city: str
    locality: str | None
    latitude: float | None
    longitude: float | None
    is_available: bool
    discovery_consent: bool
    last_donation_date: date | None

    model_config = ConfigDict(from_attributes=True)

class NearbyDonorResponse(BaseModel):
    id: int
    blood_group: BloodGroup
    city: str
    locality: str | None
    is_available: bool
    distance_km: float | None = None

    model_config = ConfigDict(from_attributes=True)
