# backend/app/api/v1/characters.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import logging

# Cấu hình logger
logger = logging.getLogger(__name__)

# Khởi tạo một router mới cho các API liên quan đến nhân vật
router = APIRouter()

# --- Pydantic Models ---
# Định nghĩa cấu trúc dữ liệu mẫu cho một nhân vật

class Character(BaseModel):
    """
    Cấu trúc dữ liệu cho một nhân vật.
    """
    id: int
    name: str
    description: str | None = None
    has_voice: bool = False

# --- Dữ liệu mẫu (Placeholder) ---
# Trong một ứng dụng thực tế, dữ liệu này sẽ đến từ database.
fake_characters_db = {
    1: {"id": 1, "name": "Gia Cát Lượng", "description": "Thừa tướng của Thục Hán.", "has_voice": True},
    2: {"id": 2, "name": "Tư Mã Ý", "description": "Đại thần của Tào Ngụy.", "has_voice": False},
}

# --- API Endpoints ---

@router.get("/", response_model=List[Character])
async def get_all_characters():
    """
    Endpoint để lấy danh sách tất cả các nhân vật.
    """
    logger.info("Fetching all characters.")
    return list(fake_characters_db.values())

@router.get("/{character_id}", response_model=Character)
async def get_character_by_id(character_id: int):
    """
    Endpoint để lấy thông tin của một nhân vật cụ thể bằng ID.
    """
    logger.info(f"Fetching character with id: {character_id}")
    character = fake_characters_db.get(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character

