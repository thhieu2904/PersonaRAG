# backend/app/main.py

import sys
from pathlib import Path

# Thêm dòng này để trỏ đến mã nguồn F5-TTS
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "f5_tts_source" / "src"))

# =================== BẮT ĐẦU ĐOẠN MÃ SỬA LỖI ENCODING ===================
# Ghi đè hàm open() mặc định của Python để luôn ưu tiên UTF-8
# Việc này giải quyết triệt để lỗi UnicodeEncodeError trên Windows
import builtins
import functools

# Lưu lại hàm open gốc
original_open = builtins.open

# Tạo hàm open mới
@functools.wraps(original_open)
def utf8_open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):
    # Nếu file được mở ở chế độ văn bản (không có 'b') và không chỉ định encoding,
    # thì mặc định là 'utf-8'
    if 'b' not in mode and encoding is None:
        encoding = 'utf-8'
    # Gọi hàm open gốc với encoding đã được đảm bảo là utf-8
    return original_open(file, mode, buffering, encoding, errors, newline, closefd, opener)

# Thay thế hàm open mặc định của toàn bộ chương trình bằng hàm mới của chúng ta
builtins.open = utf8_open
# =================== KẾT THÚC ĐOẠN MÃ SỬA LỖI ENCODING ===================


# Các dòng import còn lại của ứng dụng
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import logging

# --- 1. Import các router từ các file API của bạn ---
from app.api.v1 import chat
from app.api.v1 import characters
from app.api.v1 import voice # Đây là router voice chúng ta vừa tạo
from app.api.v1 import chat_ai # Router chat AI với GGUF models

# --- 2. Cấu hình logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 3. Khởi tạo ứng dụng FastAPI ---
app = FastAPI(
    title="Hội đồng Quân sư - Backend Service",
    description="API for RAG, Chat, and Voice Processing",
    version="1.0.0"
)

# --- 4. Cấu hình CORS (Quan trọng) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 5. Kết nối các router vào ứng dụng chính ---
api_v1_router = APIRouter()

api_v1_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_v1_router.include_router(characters.router, prefix="/characters", tags=["Characters"])
api_v1_router.include_router(voice.router, prefix="/voice", tags=["Voice"])
api_v1_router.include_router(chat_ai.router, prefix="/ai", tags=["Chat AI"])

app.include_router(api_v1_router, prefix="/api/v1")

# --- 6. Tạo một endpoint gốc để kiểm tra ---
@app.get("/")
async def root():
    return {"message": "Hội đồng Quân sư Backend Service is running!"}