from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator

class AssistantIntentEnum(str, Enum):
    VALUATION_REQUEST = "VALUATION_REQUEST"
    PROPERTY_INPUT_CLARIFICATION = "PROPERTY_INPUT_CLARIFICATION"
    VALUATION_EXPLANATION = "VALUATION_EXPLANATION"
    SUPPORTED_LOCATION_QUERY = "SUPPORTED_LOCATION_QUERY"
    GENERAL_REAL_ESTATE_QUESTION = "GENERAL_REAL_ESTATE_QUESTION"
    UNSUPPORTED_REQUEST = "UNSUPPORTED_REQUEST"

class PropertySlots(BaseModel):
    area_sqft: Optional[float] = Field(
        default=None,
        gt=0,
        le=50000,
        description="Property area in square feet"
    )
    bhk: Optional[int] = Field(
        default=None,
        ge=1,
        le=20,
        description="Number of bedrooms (BHK)"
    )
    latitude: Optional[float] = Field(
        default=None,
        ge=6.0,
        le=38.0,
        description="Geographical latitude within India"
    )
    longitude: Optional[float] = Field(
        default=None,
        ge=68.0,
        le=98.0,
        description="Geographical longitude within India"
    )
    city: Optional[str] = Field(
        default=None,
        description="City or municipality name"
    )
    posted_by: Optional[str] = Field(
        default=None,
        description="Listing channel: Owner, Dealer, or Builder"
    )
    rera: Optional[int] = Field(
        default=None,
        ge=0,
        le=1,
        description="RERA approval status (0 or 1)"
    )
    under_construction: Optional[int] = Field(
        default=None,
        ge=0,
        le=1,
        description="Under construction status (0 or 1)"
    )
    ready_to_move: Optional[int] = Field(
        default=None,
        ge=0,
        le=1,
        description="Ready to move status (0 or 1)"
    )
    resale: Optional[int] = Field(
        default=None,
        ge=0,
        le=1,
        description="Resale status (0 or 1)"
    )
    is_rk: Optional[int] = Field(
        default=None,
        ge=0,
        le=1,
        description="RK studio apartment flag (0 or 1)"
    )

    @field_validator("posted_by")
    @classmethod
    def normalize_posted_by(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = str(v).strip().title()
        if cleaned in {"Owner", "Dealer", "Builder"}:
            return cleaned
        return "Owner"

    @field_validator("city")
    @classmethod
    def normalize_city(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return str(v).strip().lower()

class AssistantLLMOutput(BaseModel):
    intent: AssistantIntentEnum = Field(
        default=AssistantIntentEnum.GENERAL_REAL_ESTATE_QUESTION,
        description="Classified conversation intent"
    )
    reply: str = Field(
        ...,
        description="Natural language reply or clarification question"
    )
    tool_call: Optional[str] = Field(
        default=None,
        description="Name of the requested tool (if any)"
    )
    slots: PropertySlots = Field(
        default_factory=PropertySlots,
        description="Extracted property attributes"
    )
    missing_slots: List[str] = Field(
        default_factory=list,
        description="List of mandatory slots still required before valuation"
    )

class AssistantChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User message in natural language or Hinglish",
        examples=["I want to estimate the price of a 1500 sqft 3 BHK flat in Bangalore."]
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Existing session UUID. If null, a new session is initialized."
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("User message cannot be empty or whitespace only.")
        return cleaned

class AssistantToolResult(BaseModel):
    tool_name: str
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class AssistantChatResponse(BaseModel):
    session_id: str = Field(
        ...,
        description="Session identifier"
    )
    reply: str = Field(
        ...,
        description="Assistant response text"
    )
    intent: AssistantIntentEnum = Field(
        ...,
        description="Identified user intent"
    )
    tool_called: Optional[str] = Field(
        default=None,
        description="Tool executed by the capability router"
    )
    tool_result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Result data returned by the executed capability"
    )
    slots: PropertySlots = Field(
        default_factory=PropertySlots,
        description="Current accumulated property slots in the session"
    )
    missing_slots: List[str] = Field(
        default_factory=list,
        description="Missing mandatory slots required to complete valuation"
    )
    is_valuation_complete: bool = Field(
        default=False,
        description="True if an authoritative valuation was computed and returned"
    )
    model_name: str = Field(
        default="Qwen2.5-3B-Instruct (GGUF Q4_K_M)",
        description="Language AI model or provider name"
    )
    created_at: str = Field(
        ...,
        description="ISO timestamp of response generation"
    )

class AssistantResetResponse(BaseModel):
    session_id: str
    status: str = "reset_success"
    message: str = "Assistant session and accumulated property slots have been successfully cleared."

class AssistantHealthResponse(BaseModel):
    status: str
    provider_type: str
    model_loaded: bool
    model_path: str
    active_sessions: int
