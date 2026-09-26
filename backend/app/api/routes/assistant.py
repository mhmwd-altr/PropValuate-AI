import logging
from fastapi import APIRouter, status, HTTPException
from ...schemas.assistant import (
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantResetResponse,
    AssistantHealthResponse,
)
from ...services.assistant_service import assistant_service
from ...services.session_manager import session_manager
from ...core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assistant", tags=["Language AI Assistant"])

@router.post(
    "",
    response_model=AssistantChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with PropValuate AI Assistant",
    description=(
        "Conversational Language AI Assistant for Indian residential real estate. "
        "Extracts property parameters, manages multi-turn slot filling, resolves "
        "supported locations, and executes authoritative Valuation Engine V2 tools."
    ),
)
async def chat_with_assistant(request: AssistantChatRequest) -> AssistantChatResponse:
    try:
        return assistant_service.process_message(request)
    except ValueError as ve:
        logger.warning(f"Validation error in assistant chat: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except Exception as e:
        logger.exception(f"Unhandled error in assistant chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request with the AI Assistant."
        )

@router.post(
    "/reset",
    response_model=AssistantResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset Assistant Session",
    description="Resets the conversation history and accumulated property slots for a session.",
)
async def reset_assistant_session(session_id: str) -> AssistantResetResponse:
    success = session_manager.reset_session(session_id)
    if success:
        return AssistantResetResponse(
            session_id=session_id,
            status="reset_success",
            message="Session history and property slots successfully reset."
        )
    return AssistantResetResponse(
        session_id=session_id,
        status="session_not_found",
        message="Session was not active or already expired."
    )

@router.get(
    "/health",
    response_model=AssistantHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Language AI Health & Readiness",
    description="Returns the operational status, loaded model name, and active session count.",
)
async def assistant_health() -> AssistantHealthResponse:
    provider = assistant_service.provider
    return AssistantHealthResponse(
        status="healthy" if provider.is_loaded else "degraded",
        provider_type=settings.LLM_PROVIDER_TYPE,
        model_loaded=provider.is_loaded,
        model_path=str(settings.LLM_MODEL_PATH),
        active_sessions=session_manager.get_active_sessions_count(),
    )
