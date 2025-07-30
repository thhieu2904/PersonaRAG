# backend/app/api/v1/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

# Cấu hình logger
logger = logging.getLogger(__name__)

# Khởi tạo một router mới cho các API liên quan đến chat
router = APIRouter()

# --- Pydantic Models ---
# Định nghĩa cấu trúc dữ liệu cho request và response

class ChatRequest(BaseModel):
    """
    Cấu trúc dữ liệu cho một yêu cầu chat từ frontend.
    """
    message: str
    character_name: str
    session_id: str | None = None # Tùy chọn: để quản lý lịch sử hội thoại

class ChatResponse(BaseModel):
    """
    Cấu trúc dữ liệu cho một câu trả lời từ backend.
    """
    reply: str
    session_id: str | None = None

# --- API Endpoint ---

@router.post("/", response_model=ChatResponse)
async def handle_chat_message(request: ChatRequest):
    """
    Endpoint chính để xử lý tin nhắn chat.
    Hiện tại, đây là một placeholder. Bạn sẽ cần tích hợp logic của
    RAG agent (tác tử truy xuất-sinh) của mình vào đây.
    """
    try:
        logger.info(f"Received chat request for character '{request.character_name}': '{request.message}'")
        
        # --- TODO: TÍCH HỢP LOGIC RAG CỦA BẠN Ở ĐÂY ---
        # 1. Lấy context từ RAG agent dựa trên `request.message` và `request.character_name`.
        # 2. Xây dựng prompt hoàn chỉnh.
        # 3. Gọi mô hình ngôn ngữ (LLM) để sinh ra câu trả lời.
        
        # Đây là một câu trả lời mẫu để hệ thống có thể chạy được
        placeholder_reply = f"Đây là câu trả lời mẫu từ {request.character_name} cho câu hỏi của bạn về: '{request.message[:20]}...'"
        
        return ChatResponse(reply=placeholder_reply, session_id=request.session_id)

    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred while processing the chat message.")

