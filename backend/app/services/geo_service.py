import math
from typing import Dict, Optional, Tuple, Set

# Valid Geographic Bounding Box for India
INDIA_LAT_MIN = 6.0
INDIA_LAT_MAX = 38.0
INDIA_LON_MIN = 68.0
INDIA_LON_MAX = 98.0

# Exact Major Indian Metro Coordinates used in Phase 3 Valuation Engine V2
METRO_CENTERS: Dict[str, Tuple[float, float]] = {
    "mumbai": (18.9220, 72.8347),
    "delhi": (28.6304, 77.2177),
    "bangalore": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
}

# The exact 39 recognized municipality categories in the V2 candidate model + 'other'
TOP_CITIES_V2: Set[str] = {
    "agra",
    "aurangabad",
    "bangalore",
    "bhopal",
    "bhubaneswar",
    "chennai",
    "coimbatore",
    "dehradun",
    "durgapur",
    "faridabad",
    "gandhinagar",
    "ghaziabad",
    "goa",
    "gurgaon",
    "guwahati",
    "gwalior",
    "jaipur",
    "jamnagar",
    "jamshedpur",
    "kochi",
    "kolkata",
    "lalitpur",
    "lucknow",
    "maharashtra",
    "mohali",
    "mumbai",
    "nagpur",
    "palghar",
    "patna",
    "raigad",
    "rajkot",
    "ranchi",
    "secunderabad",
    "siliguri",
    "sonipat",
    "surat",
    "thrissur",
    "vijayawada",
    "visakhapatnam",
}

# Common name aliases mapped to standardized training categories
CITY_ALIASES: Dict[str, str] = {
    "bengaluru": "bangalore",
    "gurugram": "gurgaon",
    "bombay": "mumbai",
    "calcutta": "kolkata",
    "madras": "chennai",
    "new delhi": "other",
    "new-delhi": "other",
    "delhi": "other",  # In the training dataset, Delhi listings were mapped to specific NCR towns or other
    "cochin": "kochi",
    "trivandrum": "other",
    "pune": "other",
    "ahmedabad": "other",
    "hyderabad": "other",
}

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates great-circle distance in kilometers between two coordinate pairs
    using the Haversine formula (Earth radius = 6371.0 km).
    Matches the exact training implementation in Phase 3.
    """
    r = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    # Safeguard against precision rounding exceeding 1.0
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c

def is_valid_india_coordinate(lat: float, lon: float) -> bool:
    """
    Validates whether given latitude and longitude fall within the geographical
    bounding box of India.
    """
    if lat is None or lon is None:
        return False
    if math.isnan(lat) or math.isnan(lon) or math.isinf(lat) or math.isinf(lon):
        return False
    return (INDIA_LAT_MIN <= lat <= INDIA_LAT_MAX) and (INDIA_LON_MIN <= lon <= INDIA_LON_MAX)

def calculate_metro_distances(lat: float, lon: float) -> Dict[str, float]:
    """
    Computes distances to key metros and finds distance to nearest tier-1 metro core.
    
    Returns:
        Dict with keys:
            - dist_mumbai_km
            - dist_delhi_km
            - dist_bangalore_km
            - dist_nearest_metro_km
    """
    dist_mumbai = haversine_distance(lat, lon, *METRO_CENTERS["mumbai"])
    dist_delhi = haversine_distance(lat, lon, *METRO_CENTERS["delhi"])
    dist_bangalore = haversine_distance(lat, lon, *METRO_CENTERS["bangalore"])
    
    all_metro_dists = [
        haversine_distance(lat, lon, coords[0], coords[1])
        for coords in METRO_CENTERS.values()
    ]
    dist_nearest = min(all_metro_dists)
    
    return {
        "dist_mumbai_km": round(dist_mumbai, 2),
        "dist_delhi_km": round(dist_delhi, 2),
        "dist_bangalore_km": round(dist_bangalore, 2),
        "dist_nearest_metro_km": round(dist_nearest, 2),
    }

def normalize_city_group(city_name: Optional[str]) -> str:
    """
    Normalizes and maps a raw city string into the approved V2 categorical group.
    
    Processing:
        1. Strips whitespace, lowers case.
        2. Checks aliases dictionary.
        3. Checks if present in TOP_CITIES_V2.
        4. Defaults to 'other' if not in top cities.
    """
    if not city_name or not isinstance(city_name, str):
        return "other"
    
    cleaned = city_name.strip().lower()
    
    # Handle aliases
    if cleaned in CITY_ALIASES:
        cleaned = CITY_ALIASES[cleaned]
        
    if cleaned in TOP_CITIES_V2:
        return cleaned
    
    return "other"
