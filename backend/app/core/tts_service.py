# backend/app/core/tts_service.py (Đã cập nhật)
import os
import sys
import tempfile
import logging
from pathlib import Path

# Thêm đường dẫn đến F5-TTS-Vietnamese-100h
current_dir = Path(__file__).resolve().parent.parent.parent
f5_tts_path = current_dir / "F5-TTS-Vietnamese-100h"
sys.path.insert(0, str(f5_tts_path))

# Import config
from .tts_config import TTSConfig

# Thư viện F5-TTS
from huggingface_hub import login
from cached_path import cached_path
from vinorm import TTSnorm
import soundfile as sf

from f5_tts.model import DiT
from f5_tts.infer.utils_infer import (
    load_vocoder,
    load_model,
    preprocess_ref_audio_text,
    infer_process,
)

logger = logging.getLogger(__name__)

class TTSService:
    """
    Dịch vụ quản lý việc tải mô hình F5-TTS và tạo giọng nói.
    """
    def __init__(self, temp_audio_dir: str = None):
        """Khởi tạo TTS Service với cấu hình từ TTSConfig"""
        # Sử dụng cấu hình từ TTSConfig
        self.config = TTSConfig
        self.temp_dir = temp_audio_dir or self.config.TEMP_AUDIO_DIR
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        self.vocoder = None
        self.model = None
        self.available_characters: dict = {}
        
        # Tạo các thư mục cần thiết
        self.config.create_directories()
        
        # Thiết lập giọng nói mặc định và tải mô hình
        self._setup_default_voices()
        self._load_models()

    def _setup_default_voices(self):
        """Thiết lập các giọng nói có sẵn từ thư mục audio_samples."""
        audio_samples_dir = self.config.AUDIO_SAMPLES_DIR
        
        # Tìm các file audio có sẵn (không cần file .txt transcript)
        if audio_samples_dir.exists():
            for audio_file in audio_samples_dir.glob("*.wav"):
                character_name = audio_file.stem  # Lấy tên file không có extension
                self.available_characters[character_name] = str(audio_file)
                logger.info(f"Đã thêm giọng nói: {character_name} -> {audio_file}")
        
        # Nếu không có file nào
        if not self.available_characters:
            logger.warning("Không tìm thấy file audio mẫu nào trong thư mục audio_samples.")
            logger.info(f"Hãy thêm file .wav vào: {audio_samples_dir}")
            logger.info("Note: Không cần file .txt transcript - mô hình sẽ tự động nhận diện.")

    def _load_models(self):
        """Tải mô hình F5-TTS và Vocoder khi khởi động."""
        try:
            # Đảm bảo device consistency
            device = self.config.get_device()
            logger.info(f"Sử dụng device: {device}")
            
            logger.info("Đang tải Vocoder...")
            self.vocoder = load_vocoder(
                vocoder_name=self.config.VOCODER_NAME,
                device=device
            )
            logger.info("Tải Vocoder thành công.")

            logger.info("Đang tải mô hình F5-TTS...")
            model_paths = self.config.get_model_paths()
            
            self.model = load_model(
                DiT,
                self.config.MODEL_CONFIG,
                ckpt_path=model_paths["model_path"],
                vocab_file=model_paths["vocab_path"],
                device=device
            )
            logger.info("Tải mô hình F5-TTS thành công.")
        except Exception as e:
            logger.error(f"Lỗi nghiêm trọng khi tải mô hình AI: {e}", exc_info=True)
            raise e

    def _post_process_text(self, text: str) -> str:
        """Hàm dọn dẹp văn bản theo app.py gốc."""
        text = " " + text + " "
        text = text.replace(" . . ", " . ")
        text = " " + text + " "
        text = text.replace(" .. ", " . ")
        text = " " + text + " "
        text = text.replace(" , , ", " , ")
        text = " " + text + " "
        text = text.replace(" ,, ", " , ")
        text = " " + text + " "
        text = text.replace('"', "")
        return " ".join(text.split())

    def _normalize_vietnamese_text(self, text: str) -> str:
        """Chuẩn hóa văn bản tiếng Việt cho TTS với fix encoding."""
        try:
            # Fix encoding issue cho Windows
            import sys
            if sys.platform == "win32":
                # Thử encode/decode để tránh lỗi charmap
                try:
                    text.encode('utf-8').decode('utf-8')
                    normalized_text = TTSnorm(text)
                    logger.info(f"Đã chuẩn hóa văn bản tiếng Việt: '{text}' -> '{normalized_text}'")
                    return normalized_text
                except (UnicodeError, UnicodeEncodeError, UnicodeDecodeError):
                    logger.warning(f"TTSnorm encoding issue với Windows. Sử dụng văn bản gốc.")
                    return text.strip()
            else:
                normalized_text = TTSnorm(text)
                logger.info(f"Đã chuẩn hóa văn bản tiếng Việt: '{text}' -> '{normalized_text}'")
                return normalized_text
        except Exception as e:
            logger.warning(f"Không thể chuẩn hóa văn bản với TTSnorm: {e}. Sử dụng văn bản gốc.")
            return text.strip()

    def add_character_voice(self, character_name: str, reference_audio_path: str):
        """Lưu đường dẫn đến file audio mẫu cho một nhân vật."""
        if not Path(reference_audio_path).exists():
            logger.warning(f"File audio tham chiếu cho '{character_name}' không tồn tại tại: {reference_audio_path}")
            return
        self.available_characters[character_name] = reference_audio_path
        logger.info(f"Đã thêm giọng nói tham chiếu cho nhân vật: '{character_name}'")

    def get_available_characters(self) -> list[str]:
        """Lấy danh sách các nhân vật đã có giọng nói."""
        return list(self.available_characters.keys())

    def synthesize_speech(self, text: str, character_name: str, speed: float = 1.0) -> str:
        """
        Tạo giọng nói từ văn bản, sử dụng audio mẫu của nhân vật.
        Implementation giống app.py gốc với device consistency fix.
        """
        # Kiểm tra độ dài văn bản
        if not self.config.validate_text_length(text):
            raise ValueError(f"Văn bản quá dài. Tối đa {self.config.MAX_TEXT_LENGTH} từ hoặc {self.config.MAX_CHAR_LENGTH} ký tự.")
        
        if character_name not in self.available_characters:
            raise ValueError(f"Nhân vật '{character_name}' chưa được thiết lập giọng nói.")
        
        reference_audio_path = self.available_characters[character_name]
            
        try:
            # 1. Tiền xử lý âm thanh - GIỐNG APP.PY GỐC: truyền empty string cho ref_text
            ref_audio, ref_text = preprocess_ref_audio_text(reference_audio_path, "")

            # 2. Chuẩn hóa và xử lý văn bản - GIỐNG APP.PY GỐC
            normalized_text = self._normalize_vietnamese_text(text)
            processed_text = self._post_process_text(normalized_text)

            # 3. Chạy mô hình để tạo giọng nói - GIỐNG APP.PY GỐC với device fix
            logger.info(f"Bắt đầu tạo giọng nói cho '{character_name}' với văn bản: '{processed_text}'...")
            
            # Device consistency check
            device = self.config.get_device()
            logger.info(f"Inference device: {device}")
            
            try:
                final_wave, final_sample_rate, spectrogram = infer_process(
                    ref_audio, 
                    ref_text.lower(), 
                    processed_text.lower(), 
                    self.model, 
                    self.vocoder, 
                    speed=speed
                )
            except RuntimeError as device_error:
                if "device" in str(device_error).lower():
                    logger.warning(f"Device error với {device}, thử lại với CPU...")
                    # Fallback to CPU và update config
                    self.config.set_device("cpu")
                    import torch
                    self.model = self.model.to("cpu")
                    self.vocoder = self.vocoder.to("cpu") if hasattr(self.vocoder, 'to') else self.vocoder
                    
                    final_wave, final_sample_rate, spectrogram = infer_process(
                        ref_audio, 
                        ref_text.lower(), 
                        processed_text.lower(), 
                        self.model, 
                        self.vocoder, 
                        speed=speed
                    )
                    logger.info("Thành công với CPU fallback")
                else:
                    raise device_error
            
            # 4. Lưu file audio vào thư mục tạm
            with tempfile.NamedTemporaryFile(
                delete=False, 
                suffix=".wav", 
                dir=self.temp_dir,
                prefix=f"{character_name}_"
            ) as tmp_file:
                output_path = tmp_file.name
                sf.write(output_path, final_wave, final_sample_rate)
            
            logger.info(f"Đã tạo thành công file audio tại: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Lỗi khi tạo giọng nói cho '{character_name}': {e}", exc_info=True)
            raise

    def cleanup_temp_files(self):
        """Xóa tất cả các file trong thư mục audio tạm."""
        logger.info(f"Đang dọn dẹp thư mục tạm: {self.temp_dir}")
        for f in self.temp_dir.glob("*"):
            if f.is_file():
                os.unlink(f)