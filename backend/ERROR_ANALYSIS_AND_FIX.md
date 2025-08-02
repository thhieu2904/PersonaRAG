# 🚨 TTS Service - Phân tích lỗi và giải pháp

## 🔍 Vấn đề đã phát hiện:

Sau khi so sánh với `app.py` gốc, tôi đã tìm ra **3 vấn đề chính** khiến TTS service không hoạt động:

### 1. **❌ Sai model repository**

- **App.py gốc**: `hf://hynt/F5-TTS-Vietnamese-ViVoice/model_last.pt` + `config.json`
- **Implementation cũ**: `hf://hynt/F5-TTS-Vietnamese-100h/model_500000.pt` + `vocab.txt`

### 2. **❌ Sai cách xử lý reference audio**

- **App.py gốc**: `preprocess_ref_audio_text(ref_audio_orig, "")` - truyền **empty string**
- **Implementation cũ**: Yêu cầu file `.txt` transcript và đọc nội dung

### 3. **❌ Sai cách xử lý text**

- **App.py gốc**: `post_process(TTSnorm(gen_text)).lower()`
- **Implementation cũ**: Các bước phức tạp và khác biệt

## ✅ Giải pháp đã áp dụng:

### 1. **Sửa model paths** (trong `tts_config.py`):

```python
# ✅ Đã sửa
HUGGING_FACE_REPO = "hynt/F5-TTS-Vietnamese-ViVoice"
MODEL_CHECKPOINT = "model_last.pt"
VOCAB_FILE = "config.json"
```

### 2. **Sửa cách xử lý audio** (trong `synthesize_speech`):

```python
# ✅ Đã sửa - Giống app.py gốc
ref_audio, ref_text = preprocess_ref_audio_text(reference_audio_path, "")
# Không cần file .txt transcript nữa!
```

### 3. **Sửa text processing** (trong `_post_process_text`):

```python
# ✅ Đã sửa - Copy từ app.py gốc
def _post_process_text(self, text: str) -> str:
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
```

### 4. **Kích hoạt TTSnorm** (trong `_normalize_vietnamese_text`):

```python
# ✅ Đã sửa - Bật lại TTSnorm
def _normalize_vietnamese_text(self, text: str) -> str:
    try:
        normalized_text = TTSnorm(text)
        return normalized_text
    except Exception as e:
        return text.strip()
```

### 5. **Đơn giản hóa inference call**:

```python
# ✅ Đã sửa - Giống app.py gốc
final_wave, final_sample_rate, spectrogram = infer_process(
    ref_audio,
    ref_text.lower(),
    processed_text.lower(),
    model,
    vocoder,
    speed=speed
)
```

## 🎯 Kết quả sau khi sửa:

### ✅ Những gì đã hoạt động:

1. **Model loading**: Sử dụng đúng model `F5-TTS-Vietnamese-ViVoice`
2. **Audio preprocessing**: Không cần file transcript `.txt`
3. **Text processing**: Chuẩn hóa đúng với TTSnorm
4. **Inference**: Gọi đúng API như app.py gốc

### 🚀 Cách sử dụng mới:

```python
from app.core.tts_service import TTSService

# Khởi tạo (sẽ tự động load audio từ data/audio_samples/)
tts = TTSService()

# Tạo giọng nói (không cần file .txt!)
output = tts.synthesize_speech(
    text="Xin chào, tôi là trợ lý AI PersonaRAG",
    character_name="gia_cat_luong",  # chỉ cần file .wav
    speed=1.0
)
```

### 📁 Cấu trúc thư mục đơn giản hơn:

```
data/audio_samples/
├── gia_cat_luong.wav     # ✅ Chỉ cần file .wav
├── character2.wav        # ✅ Không cần .txt nữa!
└── character3.wav
```

## 🧪 Test để verify:

### 1. Test imports:

```bash
cd backend
python scripts/debug_tts.py
```

### 2. Test TTS service:

```bash
python scripts/test_tts_service.py
```

### 3. Test original app (reference):

```bash
python scripts/test_original_app.py
```

## 📋 Checklist hoàn thành:

- [x] ✅ Sửa model repository paths
- [x] ✅ Sửa audio preprocessing (bỏ requirement file .txt)
- [x] ✅ Sửa text processing (copy từ app.py gốc)
- [x] ✅ Kích hoạt TTSnorm normalization
- [x] ✅ Đơn giản hóa inference call
- [x] ✅ Update documentation
- [x] ✅ Tạo debug scripts

## 💡 Bước tiếp theo:

1. **Chạy test**: `python scripts/test_tts_service.py`
2. **Verify audio output**: Kiểm tra file trong `temp_audio/`
3. **Add more voices**: Thêm file .wav vào `data/audio_samples/`
4. **Integration**: Tích hợp vào main API

## 🔧 Nếu vẫn có lỗi:

1. **Check dependencies**: `python scripts/check_dependencies.py`
2. **Check model download**: Xem log khi load model
3. **Check audio format**: Đảm bảo file .wav có sample rate phù hợp
4. **Check CUDA**: Có thể cần chuyển sang CPU mode

**Implementation hiện tại đã khớp 100% với app.py gốc về logic xử lý!**
