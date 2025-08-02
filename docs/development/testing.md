# Testing Guide

## 🧪 Quick Testing

### Test TTS Service

```bash
cd backend
python test_tts_simple.py
```

Expected output:

```
🚀 PersonaRAG TTS Test Script
========================================

1. Testing server connection...
✅ Server đang chạy

2. Getting available characters...
✅ Found 2 characters: ['gia_cat_luong', 'tu_ma_y']

3. Testing voice generation...
🎤 Generating voice for 'gia_cat_luong': 'Xin chào, tôi là trợ lý AI của bạn.'
✅ Audio saved: test_output/test_gia_cat_luong_1.wav
```

### API Testing

```bash
# Test characters endpoint
curl "http://localhost:8000/api/v1/voice/characters"

# Test speech generation
curl -X POST "http://localhost:8000/api/v1/voice/generate-speech" \
     -H "Content-Type: application/json" \
     -d '{"text": "Test message", "character_name": "gia_cat_luong"}' \
     --output test.wav
```

## 🔍 Debugging

### Common Issues

1. **Server không chạy**:

   ```bash
   # Check process
   netstat -an | findstr :8000

   # Restart server
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Model loading chậm**:

   ```bash
   # Check HuggingFace cache
   ls %USERPROFILE%\.cache\huggingface\hub\

   # Clear cache if needed
   rmdir /s %USERPROFILE%\.cache\huggingface\hub\
   ```

3. **Character not found**:

   ```bash
   # Regenerate metadata
   python scripts/generate_metadata.py --force

   # Check voice directories
   ls data/voices/
   ls data/audio_samples/
   ```

### Log Analysis

```bash
# View TTS logs
tail -f logs/tts_service.log

# Check startup logs
grep "Loading" logs/tts_service.log
```

## 🎯 Performance Testing

### Memory Usage

```python
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")
```

### Response Time

```bash
# Test API response time
time curl -X POST "http://localhost:8000/api/v1/voice/generate-speech" \
     -H "Content-Type: application/json" \
     -d '{"text": "Performance test", "character_name": "gia_cat_luong"}' \
     --output perf_test.wav
```

## 📊 Test Data

### Sample Texts (Vietnamese)

```json
{
  "short": "Xin chào",
  "medium": "Hôm nay thời tiết rất đẹp.",
  "long": "Trong lịch sử Việt Nam, có nhiều nhân vật nổi tiếng đã để lại dấu ấn sâu đậm."
}
```

### Expected Results

- **Audio format**: WAV, 24kHz
- **Response time**: < 5s for short text
- **File size**: ~100KB per second of audio
