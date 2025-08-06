# backend/app/services/cloneVoice/wrapper.py
"""
F5TTS Wrapper cho PersonaRAG
Wrapper để tích hợp F5TTS API vào TTSService một cách clean
"""

import os
import sys
import tempfile
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Thêm đường dẫn cloneVoice vào sys.path để import f5_tts
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from .api import F5TTS
import soundfile as sf

logger = logging.getLogger(__name__)

class F5TTSWrapper:
    """
    Wrapper class cho F5TTS API để tích hợp với TTSService
    """
    
    def __init__(self, 
                 model_type: str = "F5-TTS",
                 device: Optional[str] = None,
                 vocoder_name: str = "vocos"):
        """
        Khởi tạo F5TTS Wrapper
        
        Args:
            model_type: Loại mô hình ("F5-TTS" hoặc "E2-TTS")
            device: Device để chạy mô hình (None = auto detect)
            vocoder_name: Tên vocoder ("vocos" hoặc "bigvgan")
        """
        self.model_type = model_type
        self.device = device
        self.vocoder_name = vocoder_name
        
        # Khởi tạo F5TTS
        self.f5tts = F5TTS(
            model_type=model_type,
            device=device,
            vocoder_name=vocoder_name
        )
        
        logger.info(f"F5TTSWrapper initialized with model_type={model_type}, device={self.f5tts.device}")
    
    def synthesize(self, 
                   ref_audio_path: str,
                   ref_text: str,
                   target_text: str,
                   speed: float = 1.0,
                   output_path: Optional[str] = None) -> str:
        """
        Tạo giọng nói từ văn bản
        
        Args:
            ref_audio_path: Đường dẫn file audio tham chiếu
            ref_text: Text tương ứng với audio tham chiếu (có thể để trống)
            target_text: Text cần tạo giọng nói
            speed: Tốc độ đọc
            output_path: Đường dẫn file output (None = tạo file tạm)
            
        Returns:
            Đường dẫn file audio đã tạo
        """
        try:
            # Tạo file output nếu không có
            if output_path is None:
                temp_dir = Path(tempfile.gettempdir()) / "f5tts_output"
                temp_dir.mkdir(exist_ok=True)
                output_path = str(temp_dir / f"output_{hash(target_text)}.wav")
            
            # Gọi F5TTS infer
            wav, sr, spect = self.f5tts.infer(
                ref_file=ref_audio_path,
                ref_text=ref_text,
                gen_text=target_text,
                speed=speed,
                file_wave=output_path,
                show_info=logger.info
            )
            
            logger.info(f"Synthesized audio saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error in F5TTSWrapper.synthesize: {e}", exc_info=True)
            raise
    
    def transcribe(self, audio_path: str, language: Optional[str] = None) -> str:
        """
        Transcribe audio file thành text
        
        Args:
            audio_path: Đường dẫn file audio
            language: Ngôn ngữ (None = auto detect)
            
        Returns:
            Text đã transcribe
        """
        try:
            return self.f5tts.transcribe(audio_path, language)
        except Exception as e:
            logger.error(f"Error in F5TTSWrapper.transcribe: {e}", exc_info=True)
            raise
    
    def get_device(self) -> str:
        """Lấy device hiện tại"""
        return self.f5tts.device
    
    def export_spectrogram(self, wav_path: str, spect_path: str):
        """Export spectrogram từ file wav"""
        try:
            wav, sr, spect = self.f5tts.infer(
                ref_file=wav_path,
                ref_text="",
                gen_text="test",
                file_spect=spect_path
            )
        except Exception as e:
            logger.error(f"Error exporting spectrogram: {e}", exc_info=True)
            raise
