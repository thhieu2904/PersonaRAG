# PersonaRAG - Quick Start Guide

## 🚀 Setup chỉ trong 5 phút

### 1. Clone và cài đặt dependencies

```bash
# Clone project
git clone https://github.com/thhieu2904/PersonaRAG.git
cd PersonaRAG

# Setup backend
cd backend
conda create -n PersonaRAG python=3.11
conda activate PersonaRAG
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install
```

### 2. Khởi động services

```bash
# Terminal 1: Start backend
cd backend
conda activate PersonaRAG
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd frontend
npm start
```

### 3. Truy cập ứng dụng

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## ⚡ Sử dụng ngay lập tức

### Test voice generation

```bash
# Test API với curl
curl -X POST "http://localhost:8000/api/v1/voice/generate-speech" \
     -H "Content-Type: application/json" \
     -d '{"text": "Xin chào các bạn", "character_name": "gia_cat_luong"}' \
     --output test_audio.wav

# Phát file audio
start test_audio.wav  # Windows
open test_audio.wav   # MacOS
aplay test_audio.wav  # Linux
```

### Kiểm tra characters có sẵn

```bash
curl "http://localhost:8000/api/v1/voice/characters"
```

## 🎤 Thêm character mới

### Cách đơn giản nhất

```bash
# 1. Tạo thư mục
mkdir -p backend/data/voices/ten_nhan_vat_moi

# 2. Copy audio files vào thư mục (.wav, 24kHz recommended)
cp path/to/your/audio1.wav backend/data/voices/ten_nhan_vat_moi/
cp path/to/your/audio2.wav backend/data/voices/ten_nhan_vat_moi/

# 3. Tạo metadata tự động
cd backend
python scripts/generate_metadata.py --character ten_nhan_vat_moi

# 4. Cấu hình voice settings
python scripts/configure_voice_settings.py preset --character ten_nhan_vat_moi

# 5. Test ngay lập tức
curl -X POST "http://localhost:8000/api/v1/voice/generate-speech" \
     -H "Content-Type: application/json" \
     -d '{"text": "Test giọng mới", "character_name": "ten_nhan_vat_moi"}' \
     --output new_voice_test.wav
```

## 🔧 Tùy chỉnh voice quality

### Điều chỉnh tốc độ đọc

```bash
# Chậm hơn (trang trọng)
python scripts/configure_voice_settings.py set \
    --character gia_cat_luong --speed 0.7

# Nhanh hơn (năng động)
python scripts/configure_voice_settings.py set \
    --character tu_ma_y --speed 0.9
```

### Điều chỉnh nghỉ giữa câu

```bash
# Nghỉ lâu hơn (sang trọng)
python scripts/configure_voice_settings.py set \
    --character gia_cat_luong --pause_scale 1.5

# Nghỉ ngắn (nhanh gọn)
python scripts/configure_voice_settings.py set \
    --character tu_ma_y --pause_scale 1.1
```

## 📱 Integration với frontend

### Trong React component

```javascript
// Gọi API từ frontend
const generateSpeech = async (text, character) => {
  const response = await fetch("/api/v1/voice/generate-speech", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text: text,
      character_name: character,
    }),
  });

  const audioBlob = await response.blob();
  const audioUrl = URL.createObjectURL(audioBlob);

  const audio = new Audio(audioUrl);
  audio.play();
};

// Sử dụng
generateSpeech("Xin chào", "gia_cat_luong");
```

## ⚠️ Troubleshooting nhanh

### Model tải chậm?

```bash
# Kiểm tra cache HuggingFace
ls ~/.cache/huggingface/hub/

# Xóa cache và download lại
rm -rf ~/.cache/huggingface/hub/models--ckpt-vietnamese*
```

### Character không tìm thấy?

```bash
# Regenerate metadata
python scripts/generate_metadata.py --force

# Check logs
tail -f logs/tts_service.log
```

### Audio quality kém?

```bash
# Check audio format
ffprobe your_audio.wav

# Convert to correct format
ffmpeg -i input.wav -ar 24000 -ac 1 -sample_fmt s16 output.wav
```

## 📖 Xem thêm

- [README.md](README.md) - Hướng dẫn chi tiết
- [Voice Settings Guide](docs/voice_settings.md) - Tùy chỉnh voice
- [API Documentation](http://localhost:8000/docs) - API reference
- [Production Setup](docs/production.md) - Deploy với Docker

---

💡 **Tip**: Lần đầu chạy sẽ mất 1-2 phút để download model từ HuggingFace. Các lần sau sẽ nhanh hơn!
