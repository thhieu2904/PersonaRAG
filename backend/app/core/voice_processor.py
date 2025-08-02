# backend/app/core/voice_processor.py
import logging
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)

class VoiceProcessor:
    """
    Class để xử lý các file âm thanh. Trong kiến trúc F5-TTS, vai trò chính
    của nó là sao chép và quản lý file audio mẫu.
    """
    
    def __init__(self, sample_rate: int = 22050):
        """
        Khởi tạo VoiceProcessor.
        Args:
            sample_rate: Tần số lấy mẫu tiêu chuẩn. F5 yêu cầu 22050Hz.
        """
        self.sample_rate = sample_rate

    def save_reference_audio(self, source_path: str, destination_path: str) -> str:
        """
        Sao chép file audio từ một đường dẫn tạm thời đến vị trí lưu trữ lâu dài.
        Đây là bước "thiết lập giọng nói" trong kiến trúc mới.
        
        Args:
            source_path: Đường dẫn file audio tạm thời do người dùng upload.
            destination_path: Đường dẫn file audio lâu dài (ví dụ: data/audio_samples/nhan_vat.wav).
            
        Returns:
            Đường dẫn tới file đã được lưu.
        """
        try:
            logger.info(f"Lưu file audio tham chiếu từ '{source_path}' đến '{destination_path}'")
            # Đảm bảo thư mục đích tồn tại
            Path(destination_path).parent.mkdir(parents=True, exist_ok=True)
            # Sao chép file
            shutil.copyfile(source_path, destination_path)
            
            # (Tùy chọn) Ở đây bạn có thể thêm các bước xử lý audio như
            # chuẩn hóa âm lượng, cắt khoảng lặng, v.v. nếu cần.
            
            logger.info(f"Đã lưu thành công file tham chiếu tại: {destination_path}")
            return destination_path
            
        except Exception as e:
            logger.error(f"Lỗi khi lưu file audio tham chiếu: {e}", exc_info=True)
            raise