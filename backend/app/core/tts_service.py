# backend/app/core/tts_service.py
import torch
import numpy as np
from TTS.api import TTS
from pathlib import Path
import logging
import json
import os
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class TTSService:
    """
    Service để quản lý việc chuyển đổi văn bản thành giọng nói (Text-to-Speech)
    sử dụng mô hình XTTSv2 cho khả năng voice cloning.
    """
    
    def __init__(self, model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2", device: str = "auto"):
        """
        Khởi tạo TTSService.
        
        Args:
            model_name: Tên hoặc đường dẫn đến mô hình TTS.
            device: Thiết bị để chạy model ('cuda', 'cpu', hoặc 'auto').
        """
        self.device = self._get_device(device)
        self.tts_model = None
        self.voice_profiles: Dict[str, Dict[str, Any]] = {}
        self.output_dir = Path("temp_audio")
        self.output_dir.mkdir(exist_ok=True)
        
        self._initialize_tts(model_name)
    
    def _get_device(self, device: str) -> str:
        """Tự động phát hiện thiết bị phù hợp (CUDA hoặc CPU)."""
        if device == "auto":
            if torch.cuda.is_available():
                logger.info("CUDA is available. Using GPU.")
                return "cuda"
            else:
                logger.info("CUDA not available. Using CPU.")
                return "cpu"
        return device
    
    def _initialize_tts(self, model_name: str):
        """Khởi tạo mô hình TTS từ Coqui-AI."""
        try:
            logger.info(f"Initializing TTS model '{model_name}' on {self.device}...")
            self.tts_model = TTS(model_name).to(self.device)
            logger.info("TTS model initialized successfully.")
        except Exception as e:
            logger.error(f"Fatal error initializing TTS model: {e}")
            raise

    def load_voice_profile(self, profile_path: str) -> Optional[Dict[str, Any]]:
        """
        Tải thông tin profile giọng nói từ một file JSON.
        
        Args:
            profile_path: Đường dẫn đến file profile .json.
            
        Returns:
            Dictionary chứa thông tin profile nếu thành công, ngược lại là None.
        """
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile = json.load(f)
            
            character_name = profile['character_name']
            # Chỉ lưu profile, không lưu đường dẫn audio ở đây
            self.voice_profiles[character_name] = profile
            
            logger.info(f"Loaded voice profile for '{character_name}' from {profile_path}")
            return profile
            
        except Exception as e:
            logger.error(f"Error loading voice profile from {profile_path}: {e}")
            return None

    def add_character_voice(self, character_name: str, sample_audio_path: str):
        """
        Thêm một giọng nói của nhân vật vào service để sẵn sàng cho việc cloning.
        
        Args:
            character_name: Tên nhân vật.
            sample_audio_path: Đường dẫn đến file audio mẫu.
        """
        if not os.path.exists(sample_audio_path):
            logger.error(f"Sample audio file not found for '{character_name}': {sample_audio_path}")
            return

        # Đảm bảo profile của nhân vật đã tồn tại trước khi thêm giọng nói
        if character_name not in self.voice_profiles:
            self.voice_profiles[character_name] = {'character_name': character_name}

        # Lưu đường dẫn audio mẫu vào profile
        self.voice_profiles[character_name]['sample_audio_path'] = sample_audio_path
        logger.info(f"Voice for '{character_name}' is ready for cloning using '{sample_audio_path}'.")

    def synthesize_speech(
        self, 
        text: str, 
        character_name: str, 
        language: str = "vi",
        speed: float = 1.0,
        reference_audio_path: Optional[str] = None
    ) -> str:
        """
        Tổng hợp giọng nói từ văn bản.
        
        Args:
            text: Văn bản cần chuyển đổi.
            character_name: Tên nhân vật có giọng nói cần sử dụng.
            language: Mã ngôn ngữ (ví dụ: 'vi' cho tiếng Việt).
            speed: Tốc độ đọc (1.0 là bình thường).
            reference_audio_path: (Tùy chọn) Đường dẫn đến file audio để
                                  "bắt chước" ngữ điệu. Nếu không có, sẽ dùng
                                  giọng mẫu mặc định của nhân vật.
                                  
        Returns:
            Đường dẫn đến file audio .wav đã được tạo.
        """
        if not self.tts_model:
            raise RuntimeError("TTS model is not initialized.")
            
        try:
            speaker_wav_path = reference_audio_path
            
            # Nếu không có audio tham chiếu động, dùng audio mẫu mặc định
            if not speaker_wav_path or not os.path.exists(speaker_wav_path):
                profile = self.voice_profiles.get(character_name)
                if not profile:
                    raise ValueError(f"Voice profile for '{character_name}' not found.")
                
                speaker_wav_path = profile.get('sample_audio_path')
                if not speaker_wav_path or not os.path.exists(speaker_wav_path):
                    raise FileNotFoundError(f"Default sample audio for '{character_name}' not found.")
            
            # Tạo file output duy nhất
            output_filename = f"{character_name}_{hash(text + str(np.random.rand()))}.wav"
            output_path = str(self.output_dir / output_filename)
            
            logger.info(f"Synthesizing speech for '{character_name}'...")
            logger.info(f" - Text: '{text[:50]}...'")
            logger.info(f" - Speaker WAV: '{speaker_wav_path}'")
            
            self.tts_model.tts_to_file(
                text=text,
                speaker_wav=speaker_wav_path,
                language=language,
                file_path=output_path,
                speed=speed,
            )
            
            logger.info(f"Speech synthesized successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error synthesizing speech for '{character_name}': {e}")
            raise

    def get_available_characters(self) -> list:
        """Lấy danh sách các nhân vật đã sẵn sàng để tạo giọng nói."""
        return [
            name for name, profile in self.voice_profiles.items() 
            if 'sample_audio_path' in profile and os.path.exists(profile['sample_audio_path'])
        ]

    def cleanup_temp_files(self, keep_recent: int = 20):
        """Dọn dẹp các file audio tạm thời đã cũ."""
        try:
            audio_files = sorted(self.output_dir.glob("*.wav"), key=os.path.getmtime)
            files_to_delete = audio_files[:-keep_recent]
            
            for file_path in files_to_delete:
                file_path.unlink()
                logger.debug(f"Deleted old audio file: {file_path}")
        except Exception as e:
            logger.error(f"Error during temp file cleanup: {e}")
