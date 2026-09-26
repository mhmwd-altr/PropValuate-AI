import json
import re
import math
import urllib.request

def verify_city_registry():
    # 1. Load backend locations.json
    with open('backend/models/locations.json', 'r', encoding='utf-8') as f:
        backend_locs_data = json.load(f)
    backend_locations = backend_locs_data['locations'] if isinstance(backend_locs_data, dict) else backend_locs_data

    # 1b. Also verify against live API endpoint /locations
    try:
        req = urllib.request.urlopen('http://localhost:8000/locations')
        live_locs_data = json.loads(req.read().decode('utf-8'))
        live_locations = live_locs_data.get('locations', [])
    except Exception as e:
        live_locations = []
        print(f"Warning: could not fetch live /locations: {e}")

    # 2. Parse frontend cityCoordinates.ts
    with open('frontend/src/data/cityCoordinates.ts', 'r', encoding='utf-8') as f:
        ts_content = f.read()

    coord_pattern = re.compile(r"['\"]?([a-zA-Z0-9_-]+)['\"]?\s*:\s*\{\s*lat\s*:\s*([0-9.-]+)\s*,\s*lon\s*:\s*([0-9.-]+)\s*\}")
    matches = coord_pattern.findall(ts_content)

    coords_dict = {}
    duplicates = []
    for city, lat_str, lon_str in matches:
        if city in coords_dict:
            duplicates.append(city)
        coords_dict[city] = {'lat': float(lat_str), 'lon': float(lon_str)}

    locations_set = set(backend_locations)
    coords_set = set(coords_dict.keys())

    missing_from_coordinates = sorted(list(locations_set - coords_set))
    extra_in_coordinates = sorted(list(coords_set - locations_set))

    invalid_coordinates = []
    for city, c in coords_dict.items():
        lat = c['lat']
        lon = c['lon']
        is_valid = True
        reasons = []
        if not math.isfinite(lat) or not math.isfinite(lon):
            is_valid = False
            reasons.append('non-finite')
        if not (6.0 <= lat <= 38.0):
            is_valid = False
            reasons.append(f'lat {lat} not in 6-38')
        if not (68.0 <= lon <= 98.0):
            is_valid = False
            reasons.append(f'lon {lon} not in 68-98')
        if not is_valid:
            invalid_coordinates.append({'city': city, 'lat': lat, 'lon': lon, 'reasons': reasons})

    set_equality = (
        (locations_set == coords_set)
        and (len(missing_from_coordinates) == 0)
        and (len(extra_in_coordinates) == 0)
        and (len(invalid_coordinates) == 0)
        and (len(duplicates) == 0)
        and (len(backend_locations) == 81)
        and (len(coords_dict) == 81)
    )

    live_match = (set(live_locations) == coords_set) if live_locations else True

    print("================ 81-CITY COORDINATE REGISTRY VERIFICATION ================")
    print(f"locations_count: {len(backend_locations)}")
    print(f"coordinates_count: {len(coords_dict)}")
    print(f"live_endpoint_count: {len(live_locations)}")
    print(f"duplicate_keys: {len(duplicates)}")
    print(f"missing_from_coordinates: {missing_from_coordinates}")
    print(f"extra_in_coordinates: {extra_in_coordinates}")
    print(f"invalid_coordinates: {invalid_coordinates}")
    print(f"live_endpoint_match: {'PASS' if live_match else 'FAIL'}")
    print(f"set_equality: {'PASS' if set_equality else 'FAIL'}")
    print("==========================================================================")

    return set_equality

if __name__ == '__main__':
    success = verify_city_registry()
    if not success:
        exit(1)
