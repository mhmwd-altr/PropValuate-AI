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


# Canonical Centroid Coordinates for all 81 Supported Locations (matches locations.json)
CITY_CENTROIDS: Dict[str, Tuple[float, float]] = {
    "agra": (27.1767, 78.0081),
    "ahmadnagar": (19.0952, 74.7480),
    "ahmedabad": (23.0225, 72.5714),
    "allahabad": (25.4358, 81.8463),
    "aurangabad": (19.8762, 75.3433),
    "badlapur": (19.1557, 73.2596),
    "bangalore": (12.9716, 77.5946),
    "belgaum": (15.8497, 74.4977),
    "bhiwadi": (28.2010, 76.8602),
    "bhiwandi": (19.2812, 73.0588),
    "bhopal": (23.2599, 77.4126),
    "bhubaneswar": (20.2961, 85.8245),
    "chandigarh": (30.7333, 76.7794),
    "chennai": (13.0827, 80.2707),
    "coimbatore": (11.0168, 76.9558),
    "dehradun": (30.3165, 78.0322),
    "durgapur": (23.5204, 87.3119),
    "ernakulam": (9.9816, 76.2999),
    "faridabad": (28.4089, 77.3178),
    "ghaziabad": (28.6692, 77.4538),
    "goa": (15.2993, 74.1240),
    "greater-noida": (28.4744, 77.5040),
    "guntur": (16.3067, 80.4365),
    "gurgaon": (28.4595, 77.0266),
    "guwahati": (26.1445, 91.7362),
    "gwalior": (26.2183, 78.1828),
    "haridwar": (29.9457, 78.1642),
    "hyderabad": (17.3850, 78.4867),
    "indore": (22.7196, 75.8577),
    "jabalpur": (23.1815, 79.9864),
    "jaipur": (26.9124, 75.7873),
    "jamshedpur": (22.8046, 86.2029),
    "jodhpur": (26.2389, 73.0243),
    "kalyan": (19.2437, 73.1355),
    "kanpur": (26.4499, 80.3319),
    "kochi": (9.9312, 76.2673),
    "kolkata": (22.5726, 88.3639),
    "kozhikode": (11.2588, 75.7804),
    "lucknow": (26.8467, 80.9462),
    "ludhiana": (30.9010, 75.8573),
    "madurai": (9.9252, 78.1198),
    "mangalore": (12.9141, 74.8560),
    "mohali": (30.7046, 76.7179),
    "mumbai": (19.0760, 72.8777),
    "mysore": (12.2958, 76.6394),
    "nagpur": (21.1458, 79.0882),
    "nashik": (19.9975, 73.7898),
    "navi-mumbai": (19.0330, 73.0297),
    "navsari": (20.9467, 72.9520),
    "nellore": (14.4426, 79.9865),
    "new-delhi": (28.6139, 77.2090),
    "noida": (28.5355, 77.3910),
    "palakkad": (10.7867, 76.6548),
    "palghar": (19.6967, 72.7647),
    "panchkula": (30.6942, 76.8606),
    "patna": (25.5941, 85.1376),
    "pondicherry": (11.9416, 79.8083),
    "pune": (18.5204, 73.8567),
    "raipur": (21.2514, 81.6296),
    "rajahmundry": (16.9910, 81.7801),
    "ranchi": (23.3441, 85.3096),
    "satara": (17.6805, 73.9958),
    "shimla": (31.1048, 77.1734),
    "siliguri": (26.7271, 88.3953),
    "solapur": (17.6599, 75.9064),
    "sonipat": (28.9288, 77.0133),
    "surat": (21.1702, 72.8311),
    "thane": (19.2183, 72.9781),
    "thrissur": (10.5276, 76.2144),
    "tirupati": (13.6288, 79.4192),
    "trichy": (10.7905, 78.7047),
    "trivandrum": (8.5241, 76.9366),
    "udaipur": (24.5854, 73.7125),
    "udupi": (13.3409, 74.7421),
    "vadodara": (22.3072, 73.1812),
    "vapi": (20.3719, 72.9113),
    "varanasi": (25.3176, 82.9739),
    "vijayawada": (16.5062, 80.6480),
    "visakhapatnam": (17.6868, 83.2185),
    "vrindavan": (27.5794, 77.6964),
    "zirakpur": (30.6456, 76.8172),
}

# Aliases mapped to coordinate slugs
COORD_ALIASES: Dict[str, str] = {
    "bengaluru": "bangalore",
    "gurugram": "gurgaon",
    "bombay": "mumbai",
    "calcutta": "kolkata",
    "madras": "chennai",
    "new delhi": "new-delhi",
    "delhi": "new-delhi",
    "cochin": "kochi",
    "greater noida": "greater-noida",
    "navi mumbai": "navi-mumbai",
}

def resolve_city_coordinates(city_name: Optional[str]) -> Optional[Tuple[float, float]]:
    """
    Resolves the canonical latitude and longitude centroid for a supported city name.
    Returns (lat, lon) tuple if found in the verified 81-city registry, or None if unsupported.
    """
    if not city_name or not isinstance(city_name, str):
        return None
    
    slug = city_name.strip().lower().replace(" ", "-")
    
    # Check direct match
    if slug in CITY_CENTROIDS:
        return CITY_CENTROIDS[slug]
    
    # Check aliases
    raw_lower = city_name.strip().lower()
    if raw_lower in COORD_ALIASES:
        canonical = COORD_ALIASES[raw_lower]
        if canonical in CITY_CENTROIDS:
            return CITY_CENTROIDS[canonical]
            
    # Try replacing hyphens with spaces or vice versa
    clean_slug = raw_lower.replace("-", " ")
    if clean_slug in COORD_ALIASES:
        canonical = COORD_ALIASES[clean_slug]
        if canonical in CITY_CENTROIDS:
            return CITY_CENTROIDS[canonical]
            
    return None
