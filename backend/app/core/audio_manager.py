# backend/app/core/audio_manager.py
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
from .voice_processor import VoiceProcessor
from .tts_service import TTSService

logger = logging.getLogger(__name__)

class AudioManager:
    """
    Lớp quản lý cấp cao, điều phối giữa việc xử lý giọng nói (VoiceProcessor)
    và việc tạo giọng nói (TTSService).
    """
    
    def __init__(self, 
                 sample_audio_dir: str = "data/audio_samples",
                 voice_profiles_dir: str = "models/voice_profiles"):
        """
        Khởi tạo AudioManager.
        
        Args:
            sample_audio_dir: Thư mục chứa các file audio mẫu (.wav).
            voice_profiles_dir: Thư mục chứa các file profile giọng nói (.json).
        """
        # Xác định đường dẫn tuyệt đối dựa trên vị trí file này
        base_path = Path(__file__).resolve().parent.parent.parent
        self.sample_audio_dir = base_path / sample_audio_dir
        self.voice_profiles_dir = base_path / voice_profiles_dir
        
        # Đảm bảo các thư mục tồn tại
        self.sample_audio_dir.mkdir(parents=True, exist_ok=True)
        self.voice_profiles_dir.mkdir(parents=True, exist_ok=True)
        
        # Khởi tạo các service con
        self.voice_processor = VoiceProcessor()
        self.tts_service = TTSService()
        
        # Tải và chuẩn bị các giọng nói đã có sẵn khi khởi động
        self._load_and_prepare_existing_voices()
    
    def _load_and_prepare_existing_voices(self):
        """
        Tải các profile .json và chuẩn bị giọng nói tương ứng cho TTS service.
        Đây là bước quan trọng khi khởi động server.
        """
        logger.info("Loading and preparing existing character voices...")
        profile_files = list(self.voice_profiles_dir.glob("*.json"))
        
        if not profile_files:
            logger.warning(f"No voice profiles found in {self.voice_profiles_dir}. "
                           f"Use the API to set up new characters.")
            return

        for profile_path in profile_files:
            try:
                # 1. Tải thông tin từ file .json
                profile = self.tts_service.load_voice_profile(str(profile_path))
                if not profile:
                    continue

                character_name = profile['character_name']
                
                # 2. Tìm file audio mẫu tương ứng
                sample_audio_path = self.sample_audio_dir / f"{character_name}.wav"
                
                # 3. Thêm giọng nói vào TTS service để sẵn sàng clone
                if sample_audio_path.exists():
                    self.tts_service.add_character_voice(character_name, str(sample_audio_path))
                else:
                    logger.warning(f"Sample audio for '{character_name}' not found at {sample_audio_path}")

            except Exception as e:
                logger.error(f"Failed to load or prepare voice from {profile_path}: {e}")
        
        logger.info(f"Finished loading. {len(self.tts_service.get_available_characters())} characters are ready.")

    def setup_character_voice(
        self, 
        character_name: str, 
        sample_audio_path: str
    ) -> Dict[str, Any]:
        """
        Thiết lập hoàn chỉnh giọng nói cho một nhân vật từ file audio mẫu.
        Bao gồm: trích xuất đặc trưng, lưu profile, và chuẩn bị cho TTS.
        
        Args:
            character_name: Tên nhân vật (duy nhất).
            sample_audio_path: Đường dẫn đến file audio mẫu tạm thời.
            
        Returns:
            Một dictionary chứa kết quả của quá trình thiết lập.
        """
        try:
            logger.info(f"Setting up new voice for character: {character_name}")
            
            # 1. Trích xuất đặc trưng giọng nói
            features = self.voice_processor.extract_voice_features(sample_audio_path)
            
            # 2. Lưu voice profile vào thư mục models
            profile_path = self.voice_profiles_dir / f"{character_name}_profile.json"
            self.voice_processor.save_voice_profile(
                features=features,
                output_path=str(profile_path),
                character_name=character_name
            )
            
            # 3. Sao chép file audio mẫu vào thư mục data để lưu trữ lâu dài
            permanent_audio_path = self.sample_audio_dir / f"{character_name}.wav"
            Path(sample_audio_path).rename(permanent_audio_path)
            logger.info(f"Saved sample audio to {permanent_audio_path}")

            # 4. Tải lại profile và chuẩn bị giọng nói cho TTS service
            self.tts_service.load_voice_profile(str(profile_path))
            self.tts_service.add_character_voice(character_name, str(permanent_audio_path))
            
            result = {
                'status': 'success',
                'character_name': character_name,
                'profile_path': str(profile_path),
                'sample_audio_path': str(permanent_audio_path),
            }
            
            logger.info(f"Successfully set up voice for '{character_name}'.")
            return result
            
        except Exception as e:
            error_msg = f"Error setting up voice for '{character_name}': {e}"
            logger.error(error_msg, exc_info=True)
            return {'status': 'error', 'error': error_msg}
    
    def generate_speech(
        self, 
        text: str, 
        character_name: str, 
        language: str = "vi",
        reference_audio_path: Optional[str] = None
    ) -> str:
        """
        Tạo file audio từ text với giọng của nhân vật.
        
        Returns:
            Đường dẫn đến file audio đã được tạo.
        """
        return self.tts_service.synthesize_speech(
            text=text,
            character_name=character_name,
            language=language,
            reference_audio_path=reference_audio_path
        )
    
    def get_character_info(self, character_name: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin voice profile của một nhân vật."""
        return self.tts_service.voice_profiles.get(character_name)
    
    def list_available_characters(self) -> List[str]:
        """Lấy danh sách tất cả các nhân vật đã sẵn sàng để tạo giọng nói."""
        return self.tts_service.get_available_characters()
    
    def cleanup(self):
        """Dọn dẹp các file audio tạm thời do TTS service tạo ra."""
        self.tts_service.cleanup_temp_files()

