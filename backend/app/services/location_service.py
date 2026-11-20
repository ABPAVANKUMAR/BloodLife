
import math


# Earth's average radius in kilometers
EARTH_RADIUS_KM = 6371.0


def calculate_distance_km(
    latitude1: float,
    longitude1: float,
    latitude2: float,
    longitude2: float
) -> float:
    """
    Calculate the distance between two geographic
    coordinates using the Haversine formula.
    """

    lat1 = math.radians(latitude1)
    lon1 = math.radians(longitude1)

    lat2 = math.radians(latitude2)
    lon2 = math.radians(longitude2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    distance = EARTH_RADIUS_KM * c

    return round(distance, 2)


def is_within_radius(
    distance_km: float,
    radius_km: float
) -> bool:
    """
    Check whether a donor is within the
    requested search radius.
    """

    if distance_km < 0 or radius_km <= 0:
        return False

    return distance_km <= radius_km
