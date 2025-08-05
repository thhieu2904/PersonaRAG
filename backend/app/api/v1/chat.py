# backend/app/api/v1/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from typing import Optional

from app.core.character_chat_service import get_character_chat_service
from app.core.rag_agent import RAGAgent
from app.models.characters import get_character_by_id

# Cấu hình logger
logger = logging.getLogger(__name__)

# Khởi tạo một router mới cho các API liên quan đến chat
router = APIRouter()

# Initialize RAG agent và chat service
_rag_agent: Optional[RAGAgent] = None
_chat_service = None

def get_rag_enabled_chat_service():
    """Get chat service with RAG integration"""
    global _rag_agent, _chat_service
    
    if _rag_agent is None:
        logger.info("Initializing RAG agent for API...")
        _rag_agent = RAGAgent()
    
    if _chat_service is None:
        logger.info("Initializing character chat service with RAG...")
        _chat_service = get_character_chat_service(_rag_agent)
    
    return _chat_service

# --- Pydantic Models ---
# Định nghĩa cấu trúc dữ liệu cho request và response

class ChatRequest(BaseModel):
    """
    Cấu trúc dữ liệu cho một yêu cầu chat từ frontend.
    """
    message: str
    character_name: str  # Will be converted to character_id
    session_id: str | None = None # Tùy chọn: để quản lý lịch sử hội thoại
    use_rag: bool = True  # Enable/disable RAG

class ChatResponse(BaseModel):
    """
    Cấu trúc dữ liệu cho một câu trả lời từ backend.
    """
    reply: str
    session_id: str | None = None
    character_id: str
    character_name: str
    contexts_used: int = 0
    response_valid: bool = True
    follow_up_questions: list = []

class StartConversationRequest(BaseModel):
    """Request to start a new conversation"""
    character_name: str
    session_id: str | None = None

class StartConversationResponse(BaseModel):
    """Response when starting a conversation"""
    greeting: str
    session_id: str
    character_id: str
    character_name: str

# --- Helper Functions ---

def get_character_id_from_name(character_name: str) -> str:
    """Convert character name to character ID"""
    name_to_id = {
        "gia_cat_luong": "zhuge_liang",
        "zhuge_liang": "zhuge_liang",
        "tu_ma_y": "sima_yi", 
        "sima_yi": "sima_yi"
    }
    
    # Normalize name
    normalized_name = character_name.lower().replace(" ", "_")
    return name_to_id.get(normalized_name, "zhuge_liang")  # Default to Zhuge Liang

# --- API Endpoints ---

@router.post("/start", response_model=StartConversationResponse)
async def start_conversation(request: StartConversationRequest):
    """
    Start a new conversation with a character
    """
    try:
        chat_service = get_rag_enabled_chat_service()
        character_id = get_character_id_from_name(request.character_name)
        
        # Get character info
        character = get_character_by_id(character_id)
        if not character:
            raise HTTPException(status_code=404, detail=f"Character not found: {request.character_name}")
        
        # Start conversation
        success, greeting, session_id = chat_service.start_conversation(
            character_id=character_id,
            session_id=request.session_id
        )
        
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to start conversation: {greeting}")
        
        logger.info(f"Started conversation with {character.name}, session: {session_id}")
        
        return StartConversationResponse(
            greeting=greeting,
            session_id=session_id,
            character_id=character_id,
            character_name=character.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting conversation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error starting conversation")

@router.post("/", response_model=ChatResponse)
async def handle_chat_message(request: ChatRequest):
    """
    Endpoint chính để xử lý tin nhắn chat với RAG integration.
    """
    try:
        logger.info(f"Received chat request for character '{request.character_name}': '{request.message}'")
        
        # Get services
        chat_service = get_rag_enabled_chat_service()
        character_id = get_character_id_from_name(request.character_name)
        
        # Get character info
        character = get_character_by_id(character_id)
        if not character:
            raise HTTPException(status_code=404, detail=f"Character not found: {request.character_name}")
        
        # Ensure session exists
        if not request.session_id:
            # Start new conversation if no session
            success, greeting, session_id = chat_service.start_conversation(character_id)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to create session")
        else:
            session_id = request.session_id
        
        # Chat with character using RAG
        success, response, metadata = chat_service.chat_with_character(
            character_id=character_id,
            user_message=request.message,
            session_id=session_id,
            use_rag=request.use_rag
        )
        
        if not success:
            raise HTTPException(status_code=500, detail=f"Chat failed: {response}")
        
        logger.info(f"Generated response with {metadata.get('contexts_used', 0)} RAG contexts")
        
        return ChatResponse(
            reply=response,
            session_id=session_id,
            character_id=character_id,
            character_name=character.name,
            contexts_used=metadata.get('contexts_used', 0),
            response_valid=metadata.get('response_valid', True),
            follow_up_questions=metadata.get('follow_up_questions', [])
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error processing chat message")

@router.get("/characters")
async def get_available_characters():
    """Get list of available characters"""
    try:
        chat_service = get_rag_enabled_chat_service()
        characters = chat_service.get_available_characters()
        return {"characters": characters}
    except Exception as e:
        logger.error(f"Error getting characters: {e}")
        raise HTTPException(status_code=500, detail="Error getting characters")

@router.get("/status")
async def get_system_status():
    """Get system status including RAG and model info"""
    try:
        chat_service = get_rag_enabled_chat_service()
        status = chat_service.get_model_status()
        
        # Add RAG stats
        if _rag_agent:
            rag_stats = _rag_agent.get_collection_stats()
            status["rag_stats"] = rag_stats
        
        return status
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail="Error getting system status")

@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a specific session"""
    try:
        chat_service = get_rag_enabled_chat_service()
        success = chat_service.clear_session(session_id)
        return {"success": success, "message": "Session cleared" if success else "Session not found"}
    except Exception as e:
        logger.error(f"Error clearing session: {e}")
        raise HTTPException(status_code=500, detail="Error clearing session")

