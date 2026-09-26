import logging
from typing import Dict, Any, Optional, List
from ..schemas.assistant import PropertySlots, AssistantToolResult
from .feature_service import feature_service
from .geo_service import resolve_city_coordinates
from .model_service_v2 import model_service_v2
from .location_service import location_service
from ..utils.errors import PredictionExecutionError

logger = logging.getLogger(__name__)

WHITELISTED_TOOLS = {
    "predict_property_price",
    "get_supported_locations",
}

class CapabilityRouter:
    """
    Authoritative Capability Router for Language AI.
    Executes strictly whitelisted backend project tools deterministically.
    """

    def execute_tool(
        self,
        tool_name: str,
        slots: Optional[PropertySlots] = None,
        query: Optional[str] = None
    ) -> AssistantToolResult:
        """
        Validates and executes a requested capability tool.
        Rejects any non-whitelisted tool names.
        """
        if tool_name not in WHITELISTED_TOOLS:
            logger.error(f"Unauthorized tool execution attempt: '{tool_name}'")
            return AssistantToolResult(
                tool_name=tool_name,
                status="error",
                data=None,
                error=f"Capability '{tool_name}' is not authorized or supported.",
            )

        if tool_name == "predict_property_price":
            return self._execute_valuation(slots)
        elif tool_name == "get_supported_locations":
            return self._execute_locations_query(query)

        return AssistantToolResult(
            tool_name=tool_name,
            status="error",
            data=None,
            error="Unhandled capability route.",
        )

    def _execute_valuation(self, slots: Optional[PropertySlots]) -> AssistantToolResult:
        """
        Constructs and executes an authoritative V2 property valuation.
        """
        if not slots:
            return AssistantToolResult(
                tool_name="predict_property_price",
                status="error",
                error="Property slots are missing.",
            )

        # Validate mandatory slots
        missing_fields = []
        if slots.area_sqft is None or slots.area_sqft <= 0:
            missing_fields.append("area_sqft")
        if slots.bhk is None or slots.bhk < 1:
            missing_fields.append("bhk")
        if not slots.city:
            missing_fields.append("city")

        if missing_fields:
            return AssistantToolResult(
                tool_name="predict_property_price",
                status="incomplete",
                error=f"Cannot compute valuation without mandatory fields: {', '.join(missing_fields)}",
            )

        # Resolve city coordinates
        coords = resolve_city_coordinates(slots.city)
        if not coords:
            # Check if coordinates were directly provided
            if slots.latitude and slots.longitude:
                lat, lon = slots.latitude, slots.longitude
            else:
                return AssistantToolResult(
                    tool_name="predict_property_price",
                    status="unsupported_location",
                    error=f"City '{slots.city}' is not currently in the verified 81-city registry.",
                )
        else:
            lat, lon = coords

        # Build raw request payload with safe defaults for optional fields
        raw_inputs = {
            "area_sqft": float(slots.area_sqft),
            "bhk": int(slots.bhk),
            "latitude": float(lat),
            "longitude": float(lon),
            "city": str(slots.city).strip().lower(),
            "posted_by": str(slots.posted_by) if slots.posted_by else "Owner",
            "rera": int(slots.rera) if slots.rera is not None else 1,
            "under_construction": int(slots.under_construction) if slots.under_construction is not None else 0,
            "ready_to_move": int(slots.ready_to_move) if slots.ready_to_move is not None else 1,
            "resale": int(slots.resale) if slots.resale is not None else 1,
            "is_rk": int(slots.is_rk) if slots.is_rk is not None else 0,
        }

        try:
            # Feature engineering
            features = feature_service.construct_v2_features(raw_inputs)
            # Authoritative V2 inference
            predicted_inr = model_service_v2.predict(features)
            predicted_lakhs = round(predicted_inr / 100000.0, 2)
            rate_per_sqft = round(predicted_inr / float(slots.area_sqft), 2)

            result_data = {
                "predicted_price": round(predicted_inr, 2),
                "predicted_price_lakhs": predicted_lakhs,
                "rate_per_sqft": rate_per_sqft,
                "currency": "INR",
                "model_version": "2.0.0",
                "model_name": "Valuation Engine V2 (HistGradientBoosting)",
                "engineered_features": {
                    "area_per_bhk": features["area_per_bhk"],
                    "dist_nearest_metro_km": features["dist_nearest_metro_km"],
                    "dist_mumbai_km": features["dist_mumbai_km"],
                    "dist_delhi_km": features["dist_delhi_km"],
                    "dist_bangalore_km": features["dist_bangalore_km"],
                    "city_grouped": features["city_grouped"],
                },
                "property_details": {
                    "area_sqft": raw_inputs["area_sqft"],
                    "bhk": raw_inputs["bhk"],
                    "city": raw_inputs["city"].title(),
                    "posted_by": raw_inputs["posted_by"],
                    "rera": bool(raw_inputs["rera"]),
                    "ready_to_move": bool(raw_inputs["ready_to_move"]),
                    "resale": bool(raw_inputs["resale"]),
                    "is_rk": bool(raw_inputs["is_rk"]),
                },
            }

            return AssistantToolResult(
                tool_name="predict_property_price",
                status="success",
                data=result_data,
                error=None,
            )

        except Exception as e:
            logger.exception(f"Error during capability router valuation execution: {str(e)}")
            return AssistantToolResult(
                tool_name="predict_property_price",
                status="error",
                data=None,
                error=f"Valuation engine error: {str(e)}",
            )

    def _execute_locations_query(self, query: Optional[str] = None) -> AssistantToolResult:
        """
        Retrieves the verified 81-city location list.
        """
        try:
            all_locations = location_service.get_locations()
            if query:
                q_clean = query.strip().lower()
                filtered = [loc for loc in all_locations if q_clean in loc.lower()]
            else:
                filtered = all_locations

            return AssistantToolResult(
                tool_name="get_supported_locations",
                status="success",
                data={
                    "locations": filtered,
                    "total_count": len(filtered),
                    "is_filtered": bool(query),
                },
                error=None,
            )
        except Exception as e:
            logger.error(f"Error retrieving locations: {str(e)}")
            return AssistantToolResult(
                tool_name="get_supported_locations",
                status="error",
                data=None,
                error=f"Location service error: {str(e)}",
            )

capability_router = CapabilityRouter()
