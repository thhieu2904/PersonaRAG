import sys
from pathlib import Path
import logging

# Thêm dòng này để script có thể tìm thấy các module trong thư mục 'app'
# Nó sẽ thêm thư mục gốc của dự án (hoi-dong-quan-su) vào đường dẫn tìm kiếm của Python
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Bây giờ mới có thể import VoiceProcessor
from app.core.voice_processor import VoiceProcessor

# Cấu hình logging để xem tiến trình
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Định nghĩa các đường dẫn
SOURCE_AUDIO_DIR = project_root / "data" / "audio_samples"
OUTPUT_PROFILE_DIR = project_root / "models" / "voice_profiles"

def process_all_voices():
    """
    Quét tất cả các file audio trong thư mục nguồn,
    trích xuất đặc trưng và lưu thành file profile .json.
    """
    if not SOURCE_AUDIO_DIR.exists():
        logging.error(f"Thư mục nguồn không tồn tại: {SOURCE_AUDIO_DIR}")
        return

    # Tạo thư mục output nếu chưa có
    OUTPUT_PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    voice_processor = VoiceProcessor()
    
    logging.info(f"Bắt đầu quét giọng nói từ: {SOURCE_AUDIO_DIR}")
    
    audio_files = list(SOURCE_AUDIO_DIR.glob("*.wav"))
    if not audio_files:
        logging.warning("Không tìm thấy file .wav nào trong thư mục nguồn.")
        return

    for audio_path in audio_files:
        try:
            # Lấy tên nhân vật từ tên file (ví dụ: 'gia_cat_luong.wav' -> 'gia_cat_luong')
            character_name = audio_path.stem

            logging.info(f"Đang xử lý nhân vật: {character_name}...")

            # 1. Trích xuất đặc trưng giọng nói
            features = voice_processor.extract_voice_features(str(audio_path))
            
            # 2. Lưu voice profile
            profile_path = OUTPUT_PROFILE_DIR / f"{character_name}_profile.json"
            voice_processor.save_voice_profile(
                features=features,
                output_path=str(profile_path),
                character_name=character_name
            )
            
            logging.info(f"Đã lưu thành công profile cho {character_name} tại {profile_path}")

        except Exception as e:
            logging.error(f"Lỗi khi xử lý file {audio_path}: {e}")
            
    logging.info("Hoàn tất xử lý tất cả giọng nói!")

if __name__ == "__main__":
    process_all_voices()
