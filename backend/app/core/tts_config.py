# backend/app/core/tts_config.py
"""
Cấu hình cho TTS Service
"""
import os
from pathlib import Path
from typing import Dict, Any

class TTSConfig:
    """Cấu hình cho TTS Service"""
    
    # Đường dẫn cơ bản
    BASE_PATH = Path(__file__).resolve().parent.parent.parent
    CLONE_VOICE_PATH = BASE_PATH / "app" / "services" / "cloneVoice"
    AUDIO_SAMPLES_DIR = BASE_PATH / "data" / "audio_samples"
    TEMP_AUDIO_DIR = BASE_PATH / "temp_audio"
    
    # Cấu hình mô hình F5-TTS
    MODEL_CONFIG = {
        "dim": 1024,
        "depth": 22,
        "heads": 16,
        "ff_mult": 2,
        "text_dim": 512,
        "conv_layers": 4
    }
    
    # Đường dẫn mô hình trên Hugging Face
    HUGGING_FACE_REPO = "hynt/F5-TTS-Vietnamese-ViVoice"
    MODEL_CHECKPOINT = "model_last.pt"
    VOCAB_FILE = "config.json"
    
    # Cấu hình audio
    TARGET_SAMPLE_RATE = 24000
    N_MEL_CHANNELS = 100
    HOP_LENGTH = 256
    
    # Cấu hình inference với Vietnamese optimization
    DEFAULT_SPEED = 0.8  # Slower for more natural Vietnamese speech
    DEFAULT_CFG_STRENGTH = 2.0
    DEFAULT_NFE_STEP = 32
    TARGET_RMS = 0.1
    CROSS_FADE_DURATION = 0.15
    SWAY_SAMPLING_COEF = -1.0
    
    # Vietnamese speech specific settings
    VIETNAMESE_SETTINGS = {
        "temperature": 0.7,  # Voice variation
        "top_p": 0.9,  # Nucleus sampling
        "top_k": 0,  # Top-k sampling (0 = disabled)
        "repetition_penalty": 1.05,  # Prevent repetition
        "length_penalty": 1.0,  # Length control
        "pause_scale": 1.3,  # Longer pauses between phrases
        "stress_scale": 0.9,  # Softer stress on syllables
    }
    
    # Character-specific voice settings
    CHARACTER_VOICE_SETTINGS = {
        "gia_cat_luong": {
            "speed": 0.75,  # Slower, more contemplative
            "temperature": 0.65,  # More consistent tone
            "pause_scale": 1.4,  # Longer pauses for wisdom
            "stress_scale": 0.85,  # Gentle delivery
            "pitch_scale": 0.95,  # Slightly lower pitch
        },
        "tu_ma_y": {
            "speed": 0.85,  # Slightly faster, more energetic
            "temperature": 0.8,  # More variation
            "pause_scale": 1.2,  # Standard pauses
            "stress_scale": 1.0,  # Normal stress
            "pitch_scale": 1.05,  # Slightly higher pitch
        }
    }
    
    # Cấu hình device - Safe auto detect
    @staticmethod
    def _get_device():
        """Tự động phát hiện device tốt nhất"""
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        except Exception:
            # Fallback to CPU if any error
            return "cpu"
    
    DEVICE = _get_device()
    
    # Cấu hình vocoder
    VOCODER_NAME = "vocos"
    VOCODER_REPO = "charactr/vocos-mel-24khz"
    
    # Giới hạn văn bản
    MAX_TEXT_LENGTH = 1000  # số từ tối đa
    MAX_CHAR_LENGTH = 5000  # số ký tự tối đa
    
    # Cấu hình giọng nói mặc định
    DEFAULT_VOICE_TEXT = "Xin chào, đây là giọng nói mặc định."
    
    @classmethod
    def get_model_paths(cls) -> Dict[str, str]:
        """Lấy đường dẫn đến các file mô hình"""
        from cached_path import cached_path
        
        return {
            "model_path": str(cached_path(f"hf://{cls.HUGGING_FACE_REPO}/{cls.MODEL_CHECKPOINT}")),
            "vocab_path": str(cached_path(f"hf://{cls.HUGGING_FACE_REPO}/{cls.VOCAB_FILE}"))
        }
    
    @classmethod
    def get_device(cls):
        """Get current device setting"""
        return cls.DEVICE
    
    @classmethod
    def set_device(cls, device: str):
        """Override device setting"""
        cls.DEVICE = device
    
    @classmethod
    def get_inference_config(cls) -> Dict[str, Any]:
        """Lấy cấu hình cho inference"""
        return {
            "speed": cls.DEFAULT_SPEED,
            "cfg_strength": cls.DEFAULT_CFG_STRENGTH,
            "nfe_step": cls.DEFAULT_NFE_STEP,
            "target_rms": cls.TARGET_RMS,
            "cross_fade_duration": cls.CROSS_FADE_DURATION,
            "sway_sampling_coef": cls.SWAY_SAMPLING_COEF,
            "device": cls.DEVICE
        }
    
    @classmethod
    def validate_text_length(cls, text: str) -> bool:
        """Kiểm tra độ dài văn bản có hợp lệ không"""
        word_count = len(text.split())
        char_count = len(text)
        
        return word_count <= cls.MAX_TEXT_LENGTH and char_count <= cls.MAX_CHAR_LENGTH
    
    @classmethod
    def create_directories(cls):
        """Tạo các thư mục cần thiết"""
        cls.AUDIO_SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
        cls.TEMP_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
