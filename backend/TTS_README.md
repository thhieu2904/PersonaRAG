# PersonaRAG TTS Service - Hướng dẫn sử dụng

Đây là service Text-to-Speech (TTS) cho dự án PersonaRAG, sử dụng mô hình F5-TTS-Vietnamese-100h để tạo giọng nói tiếng Việt chất lượng cao với khả năng clone voice.

## 🚀 Tính năng chính

- **Clone Voice**: Tạo giọng nói giống với giọng mẫu
- **Tiếng Việt**: Hỗ trợ đầy đủ tiếng Việt với chuẩn hóa văn bản TTSnorm
- **Chất lượng cao**: Sử dụng mô hình F5-TTS được train 100+ giờ dữ liệu
- **Linh hoạt**: Điều chỉnh tốc độ, cường độ, và các tham số khác

## 📦 Cài đặt

### 1. Cài đặt dependencies

```bash
# Chạy script thiết lập (Windows)
cd backend
scripts\setup_environment.bat

# Hoặc thủ công
poetry install
```

### 2. Chuẩn bị dữ liệu giọng nói

Đặt các file audio mẫu và transcript tương ứng vào thư mục `data/audio_samples/`:

```
data/audio_samples/
├── gia_cat_luong.wav    # File audio mẫu
├── gia_cat_luong.txt    # Transcript tương ứng
├── character2.wav
├── character2.txt
...
```

**Yêu cầu file audio:**

- Format: WAV, 24kHz (khuyến nghị)
- Độ dài: 5-15 giây
- Chất lượng: Rõ ràng, ít noise
- Transcript: Văn bản chính xác của audio

## 🔧 Sử dụng

### Khởi tạo TTS Service

```python
from app.core.tts_service import TTSService

# Khởi tạo service
tts = TTSService()

# Kiểm tra giọng nói có sẵn
characters = tts.get_available_characters()
print(f"Giọng nói có sẵn: {characters}")
```

### Tạo giọng nói

```python
# Tạo audio từ văn bản
output_path = tts.synthesize_speech(
    text="Xin chào, tôi là trợ lý AI PersonaRAG",
    character_name="gia_cat_luong",
    speed=1.0
)

print(f"File audio được tạo tại: {output_path}")
```

### Thêm giọng nói mới

```python
# Thêm giọng nói từ file audio
tts.add_character_voice(
    character_name="ten_nhan_vat",
    reference_audio_path="/path/to/audio.wav"
)
```

## 🧪 Test và Debug

### Test cơ bản

```bash
cd backend
poetry run python scripts/test_tts_service.py
```

### Test từng thành phần

```python
# Test chuẩn hóa văn bản
from vinorm import TTSnorm
text = "123 số điện thoại 0901234567"
normalized = TTSnorm(text)
print(f"Chuẩn hóa: {normalized}")

# Test load mô hình
import torch
print(f"CUDA available: {torch.cuda.is_available()}")

# Test audio processing
import soundfile as sf
audio, sr = sf.read("data/audio_samples/gia_cat_luong.wav")
print(f"Audio shape: {audio.shape}, Sample rate: {sr}")
```

## ⚙️ Cấu hình

Tất cả cấu hình được quản lý trong `app/core/tts_config.py`:

```python
class TTSConfig:
    # Cấu hình mô hình
    MODEL_CONFIG = {
        "dim": 1024,
        "depth": 22,
        "heads": 16,
        # ...
    }

    # Cấu hình audio
    TARGET_SAMPLE_RATE = 24000

    # Cấu hình inference
    DEFAULT_SPEED = 1.0
    DEFAULT_CFG_STRENGTH = 2.0

    # Giới hạn văn bản
    MAX_TEXT_LENGTH = 1000  # từ
    MAX_CHAR_LENGTH = 5000  # ký tự
```

## 🚨 Troubleshooting

### Lỗi import modules

```bash
# Cài đặt lại dependencies
poetry install --no-cache

# Kiểm tra PyTorch CUDA
poetry run python -c "import torch; print(torch.cuda.is_available())"
```

### Lỗi memory (GPU)

```python
# Trong tts_config.py, thay đổi:
DEVICE = "cpu"  # Thay vì "cuda"
```

### Audio chất lượng kém

1. **Kiểm tra file audio mẫu:**

   - Chất lượng rõ ràng, ít noise
   - Độ dài 5-15 giây
   - Sample rate 24kHz

2. **Kiểm tra transcript:**

   - Chính xác 100% với audio
   - Sử dụng dấu câu đúng

3. **Điều chỉnh tham số:**

   ```python
   # Tăng CFG strength cho chất lượng tốt hơn
   TTSConfig.DEFAULT_CFG_STRENGTH = 3.0

   # Giảm speed cho rõ ràng hơn
   speed = 0.8
   ```

### Lỗi không tìm thấy mô hình

```bash
# Đăng nhập Hugging Face (nếu cần)
huggingface-cli login

# Hoặc set token
export HUGGINGFACEHUB_API_TOKEN="your_token"
```

## 📁 Cấu trúc thư mục

```
backend/
├── app/core/
│   ├── tts_service.py      # Service chính
│   ├── tts_config.py       # Cấu hình
│   └── ...
├── data/audio_samples/     # File audio mẫu
├── temp_audio/            # File audio tạm thời
├── F5-TTS-Vietnamese-100h/ # Mô hình F5-TTS
├── scripts/
│   ├── test_tts_service.py    # Test script
│   └── setup_environment.bat  # Setup script
└── pyproject.toml         # Dependencies
```

## 🤝 Đóng góp

1. Thêm giọng nói mới vào `data/audio_samples/`
2. Cải thiện cấu hình trong `tts_config.py`
3. Thêm test cases trong `scripts/test_tts_service.py`
4. Báo cáo bug và feature requests

## 📄 License

Dự án sử dụng mô hình F5-TTS-Vietnamese-100h từ Hugging Face.
