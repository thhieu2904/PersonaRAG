# backend/app/main.py
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import logging

# --- 1. Import các router từ các file API của bạn ---
# Giả sử bạn đã có các file này trong backend/app/api/v1/
# Nếu chưa có, bạn có thể tạm thời comment (thêm # ở đầu dòng) các dòng import không dùng đến.
from app.api.v1 import chat
from app.api.v1 import characters
from app.api.v1 import voice # Đây là router voice chúng ta vừa tạo

# --- 2. Cấu hình logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 3. Khởi tạo ứng dụng FastAPI ---
# Đây chính là biến "app" mà uvicorn tìm kiếm
app = FastAPI(
    title="Hội đồng Quân sư - Backend Service",
    description="API for RAG, Chat, and Voice Processing",
    version="1.0.0"
)

# --- 4. Cấu hình CORS (Quan trọng) ---
# Đoạn code này cho phép frontend (chạy ở port 3000) có thể
# gọi API của backend (chạy ở port 8000) mà không bị trình duyệt chặn.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173"], # <--- THÊM VÀO ĐÂY
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 5. Kết nối các router vào ứng dụng chính ---
# Gom tất cả router V1 vào một router lớn để dễ quản lý
api_v1_router = APIRouter()

# Thêm từng router con vào router V1 với một tiền tố (prefix) riêng
api_v1_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_v1_router.include_router(characters.router, prefix="/characters", tags=["Characters"])
api_v1_router.include_router(voice.router, prefix="/voice", tags=["Voice"])

# Thêm router V1 lớn vào ứng dụng chính
app.include_router(api_v1_router, prefix="/api/v1")

# --- 6. Tạo một endpoint gốc để kiểm tra ---
@app.get("/")
async def root():
    return {"message": "Hội đồng Quân sư Backend Service is running!"}

