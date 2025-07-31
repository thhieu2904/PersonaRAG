# backend/app/api/v1/voice.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import tempfile
import os
import logging
import shutil

# Đường dẫn import đã được sửa cho đúng với cấu trúc dự án
from app.core.audio_manager import AudioManager

# Cấu hình logger
logger = logging.getLogger(__name__)

# --- Dependency Injection ---
audio_manager_instance = AudioManager()

def get_audio_manager():
    """Dependency function để cung cấp instance AudioManager cho các endpoint."""
    return audio_manager_instance
# --------------------------

router = APIRouter()

# --- Pydantic Models ---
class TTSRequest(BaseModel):
    text: str
    character_name: str
    # THAY ĐỔI: Đổi ngôn ngữ mặc định sang "vi"
    language: str = "vi"

class VoiceSetupResponse(BaseModel):
    character_name: str
    status: str
    message: str
    profile_path: Optional[str] = None
    error: Optional[str] = None

class CharacterInfo(BaseModel):
    name: str
    has_profile: bool
    sample_audio_path: Optional[str] = None

class CharacterListResponse(BaseModel):
    total_characters: int
    characters: List[CharacterInfo]

# --- API Endpoints ---

@router.post("/setup-character-voice", response_model=VoiceSetupResponse)
async def setup_character_voice(
    character_name: str = Form(...),
    audio_file: UploadFile = File(...),
    audio_manager: AudioManager = Depends(get_audio_manager)
):
    """
    API để thiết lập giọng nói cho một nhân vật từ file audio mẫu.
    """
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {audio_file.content_type}. Please use an audio format."
        )
    
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{audio_file.filename}") as temp_file:
            shutil.copyfileobj(audio_file.file, temp_file)
            temp_path = temp_file.name
        
        result = audio_manager.setup_character_voice(
            character_name=character_name,
            sample_audio_path=temp_path
        )
        
        if result['status'] == 'success':
            return VoiceSetupResponse(
                character_name=character_name,
                status="success",
                message=f"Voice setup completed for {character_name}",
                profile_path=result.get('profile_path')
            )
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error during voice setup.'))
            
    except Exception as e:
        logger.error(f"Error in setup_character_voice: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)

@router.post("/generate-speech")
async def generate_speech(
    request: TTSRequest,
    audio_manager: AudioManager = Depends(get_audio_manager)
):
    """
    API để tạo file audio từ văn bản với giọng của nhân vật đã chọn.
    """
    try:
        if request.character_name not in audio_manager.list_available_characters():
            raise HTTPException(
                status_code=404, 
                detail=f"Character '{request.character_name}' not found. Please set up the voice first."
            )
        
        audio_path = audio_manager.generate_speech(
            text=request.text,
            character_name=request.character_name,
            language=request.language
        )
        
        return FileResponse(
            path=audio_path,
            media_type="audio/wav",
            filename=f"{request.character_name}_speech.wav"
        )
    
    except Exception as e:
        logger.error(f"Error in generate_speech: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/characters", response_model=CharacterListResponse)
async def list_characters(audio_manager: AudioManager = Depends(get_audio_manager)):
    """
    API để lấy danh sách tất cả các nhân vật đã có giọng nói sẵn sàng.
    """
    try:
        character_names = audio_manager.list_available_characters()
        character_info_list = []
        
        for char_name in character_names:
            info = audio_manager.get_character_info(char_name)
            character_info_list.append(CharacterInfo(
                name=char_name,
                has_profile=info is not None,
                sample_audio_path=info.get('sample_audio_path') if info else None
            ))
        
        return CharacterListResponse(
            total_characters=len(character_info_list),
            characters=character_info_list
        )
    
    except Exception as e:
        logger.error(f"Error in list_characters: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cleanup", status_code=200)
async def cleanup_temp_files(audio_manager: AudioManager = Depends(get_audio_manager)):
    """
    API để dọn dẹp các file audio tạm thời được tạo ra trong quá trình sử dụng.
    """
    try:
        audio_manager.cleanup()
        return {"message": "Temporary audio files cleaned up successfully."}
    
    except Exception as e:
        logger.error(f"Error during cleanup: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
