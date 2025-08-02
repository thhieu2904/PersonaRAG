# backend/app/core/audio_manager.py
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
from .voice_processor import VoiceProcessor
from .tts_service import TTSService # <-- Import service mới

logger = logging.getLogger(__name__)

class AudioManager:
    """
    Lớp quản lý cấp cao, điều phối việc lưu trữ file audio mẫu
    và gọi TTSService để tạo giọng nói.
    """
    
    def __init__(self, 
                 sample_audio_dir: str = "data/audio_samples",
                 voices_dir: str = "data/voices"):
        """Khởi tạo AudioManager."""
        base_path = Path(__file__).resolve().parent.parent.parent
        self.sample_audio_dir = base_path / sample_audio_dir
        self.voices_dir = base_path / voices_dir  # New voices directory
        self.sample_audio_dir.mkdir(parents=True, exist_ok=True)
        self.voices_dir.mkdir(parents=True, exist_ok=True)
        
        self.voice_processor = VoiceProcessor()
        self.tts_service = TTSService() # <-- Khởi tạo service mới
        
        self._load_existing_voices()
    
    def _load_existing_voices(self):
        """
        Tải các giọng nói từ cả audio_samples (legacy) và voices directory (new structure).
        """
        logger.info("Đang tải các giọng nói tham chiếu đã có...")
        
        # 1. Load from legacy audio_samples directory
        if self.sample_audio_dir.exists():
            audio_files = list(self.sample_audio_dir.glob("*.wav"))
            for audio_path in audio_files:
                try:
                    character_name = audio_path.stem
                    self.tts_service.add_character_voice(character_name, str(audio_path))
                    logger.info(f"Loaded legacy voice: {character_name}")
                except Exception as e:
                    logger.error(f"Lỗi khi tải giọng nói từ {audio_path}: {e}")
        
        # 2. Load from new voices directory structure
        if self.voices_dir.exists():
            for character_dir in self.voices_dir.iterdir():
                if character_dir.is_dir():
                    try:
                        character_name = character_dir.name
                        
                        # Check for metadata
                        metadata_file = character_dir / "metadata.json"
                        if metadata_file.exists():
                            # Load metadata to get reference audio
                            import json
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                            
                            # Look for reference.wav or first sample
                            ref_audio_path = None
                            if (character_dir / "reference.wav").exists():
                                ref_audio_path = character_dir / "reference.wav"
                            elif metadata.get('samples'):
                                first_sample = metadata['samples'][0]['file']
                                ref_audio_path = character_dir / first_sample
                            
                            if ref_audio_path and ref_audio_path.exists():
                                self.tts_service.add_character_voice(character_name, str(ref_audio_path))
                                logger.info(f"Loaded voice from metadata: {character_name} -> {ref_audio_path.name}")
                            else:
                                logger.warning(f"No reference audio found for {character_name}")
                        else:
                            # Fallback: use first .wav file found
                            audio_files = list(character_dir.glob("*.wav"))
                            if audio_files:
                                ref_audio_path = audio_files[0]
                                self.tts_service.add_character_voice(character_name, str(ref_audio_path))
                                logger.info(f"Loaded voice (fallback): {character_name} -> {ref_audio_path.name}")
                    
                    except Exception as e:
                        logger.error(f"Lỗi khi tải giọng nói từ {character_dir}: {e}")
        
        # Log summary
        total_characters = len(self.tts_service.get_available_characters())
        if total_characters == 0:
            logger.warning("Không tìm thấy file audio mẫu nào.")
            logger.info(f"Hãy thêm file .wav vào: {self.sample_audio_dir} hoặc {self.voices_dir}")
        else:
            logger.info(f"Hoàn tất. {total_characters} nhân vật đã sẵn sàng.")
            for char in self.tts_service.get_available_characters():
                logger.info(f"  - {char}")

    def setup_character_voice(
        self, 
        character_name: str, 
        temp_audio_path: str
    ) -> Dict[str, Any]:
        """
        Thiết lập giọng nói cho một nhân vật bằng cách lưu lại file audio mẫu.
        """
        try:
            logger.info(f"Thiết lập giọng nói mới cho nhân vật: {character_name}")
            
            # 1. Định nghĩa đường dẫn lưu trữ lâu dài cho file audio
            permanent_audio_path = self.sample_audio_dir / f"{character_name}.wav"
            
            # 2. Dùng VoiceProcessor để sao chép file từ temp sang vị trí chính thức
            self.voice_processor.save_reference_audio(
                source_path=temp_audio_path,
                destination_path=str(permanent_audio_path)
            )

            # 3. Thêm giọng nói mới vào TTS service để sẵn sàng sử dụng
            self.tts_service.add_character_voice(character_name, str(permanent_audio_path))
            
            result = {
                'status': 'success',
                'character_name': character_name,
                'sample_audio_path': str(permanent_audio_path),
            }
            
            logger.info(f"Thiết lập thành công giọng nói cho '{character_name}'.")
            return result
            
        except Exception as e:
            error_msg = f"Lỗi khi thiết lập giọng nói cho '{character_name}': {e}"
            logger.error(error_msg, exc_info=True)
            return {'status': 'error', 'error': error_msg}
    
    def generate_speech(self, text: str, character_name: str) -> str:
        """
        Tạo file audio từ text với giọng của nhân vật.
        """
        # Tham số language không còn cần thiết với F5-TTS-ViVoice
        return self.tts_service.synthesize_speech(
            text=text,
            character_name=character_name
        )
    
    def get_character_info(self, character_name: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin về giọng nói của một nhân vật."""
        if character_name in self.tts_service.available_characters:
            return {
                'character_name': character_name,
                'sample_audio_path': self.tts_service.available_characters[character_name]
            }
        return None
    
    def list_available_characters(self) -> List[str]:
        """Lấy danh sách tất cả các nhân vật đã sẵn sàng để tạo giọng nói."""
        return self.tts_service.get_available_characters()
    
    def cleanup(self):
        """Dọn dẹp các file audio tạm thời do TTS service tạo ra."""
        self.tts_service.cleanup_temp_files()