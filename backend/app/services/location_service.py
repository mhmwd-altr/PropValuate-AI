import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..core.config import settings
from ..utils.errors import LocationDataNotFoundError

logger = logging.getLogger(__name__)

class LocationService:
    def __init__(self, locations_path: Optional[Path] = None):
        self.locations_path = locations_path or settings.LOCATIONS_PATH
        self._locations: List[str] = []
        self._total_locations: int = 0
        self._is_loaded: bool = False

    def load(self) -> None:
        """Loads and caches the location metadata from locations.json."""
        if not self.locations_path.exists():
            logger.error(f"Locations artifact not found at: {self.locations_path}")
            raise LocationDataNotFoundError(f"Locations file not found at {self.locations_path}")
        
        try:
            with open(self.locations_path, 'r', encoding='utf-8') as f:
                data: Dict[str, Any] = json.load(f)
                
            self._locations = data.get("locations", [])
            self._total_locations = data.get("total_locations", len(self._locations))
            self._is_loaded = True
            logger.info(f"Loaded {self._total_locations} locations from {self.locations_path}")
        except Exception as e:
            logger.exception(f"Failed to parse locations artifact: {str(e)}")
            raise LocationDataNotFoundError(f"Failed to load locations: {str(e)}")

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def get_locations(self) -> List[str]:
        """Returns the list of allowed locations."""
        if not self._is_loaded:
            self.load()
        return self._locations

    def get_total_count(self) -> int:
        """Returns the total number of locations."""
        if not self._is_loaded:
            self.load()
        return self._total_locations

    def is_valid_location(self, location: str) -> bool:
        """Checks if a given location string is in the verified locations list."""
        if not self._is_loaded:
            self.load()
        return location.strip().lower() in self._locations

location_service = LocationService()
