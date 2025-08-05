# backend/app/api/v1/characters.py
from fastapi import APIRouter, HTTPException
from typing import List
import logging
from app.models.characters import get_all_characters, get_character_by_id

# Cấu hình logger
logger = logging.getLogger(__name__)

# Khởi tạo một router mới cho các API liên quan đến nhân vật
router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_characters():
    """
    Lấy danh sách tất cả nhân vật có sẵn.
    """
    try:
        # Lấy characters từ models
        characters_dict = get_all_characters()
        
        # Convert to list and API format
        result = []
        for char in characters_dict.values():
            result.append({
                "character_id": char.id,  # Map id to character_id
                "name": char.name,
                "description": char.description,
                "character_type": char.character_type,
                "origin": char.origin,
                "birth_year": char.birth_year,
                "death_year": char.death_year,
                "personality_traits": char.personality_traits,
                "expertise": char.expertise,
                "advice_style": char.advice_style,
                "speaking_style": char.speaking_style,
                "is_active": char.is_active
            })
        
        logger.info(f"Returning {len(result)} characters")
        return result
        
    except Exception as e:
        logger.error(f"Error getting characters: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{character_id}")
async def get_character(character_id: str):
    """
    Lấy thông tin chi tiết một nhân vật theo ID.
    """
    try:
        character = get_character_by_id(character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        return {
            "character_id": character.id,  # Map id to character_id
            "name": character.name,
            "description": character.description,
            "character_type": character.character_type,
            "origin": character.origin,
            "birth_year": character.birth_year,
            "death_year": character.death_year,
            "personality_traits": character.personality_traits,
            "expertise": character.expertise,
            "famous_quotes": character.famous_quotes,
            "advice_style": character.advice_style,
            "speaking_style": character.speaking_style,
            "is_active": character.is_active
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting character {character_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

