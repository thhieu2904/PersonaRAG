# 🚨 Device Error Fix Guide

## Vấn đề: CUDA device mismatch

```
RuntimeError: Expected all tensors to be on the same device,
but found at least two devices, cpu and cuda:0!
```

## ✅ Giải pháp đã áp dụng:

### 1. **Auto device detection** (trong `tts_config.py`):

```python
@classmethod
def get_device(cls):
    import torch
    if torch.cuda.is_available():
        return "cuda"
    else:
        return "cpu"
```

### 2. **TTSnorm encoding fix** (trong `tts_service.py`):

- Fix encoding issue cho Windows
- Fallback to raw text nếu TTSnorm fail

### 3. **CPU fallback** (trong `synthesize_speech`):

- Tự động chuyển sang CPU nếu CUDA có lỗi
- Device consistency check

## 🧪 Test options:

### Option 1: Test với auto device detection

```bash
poetry run python scripts/test_tts_service.py
```

### Option 2: Test với force CPU mode (an toàn)

```bash
poetry run python scripts/test_tts_cpu.py
```

### Option 3: Test với manual device setting

```python
# Trong tts_config.py, thay đổi:
DEVICE = "cpu"  # Force CPU mode
```

## 📋 Troubleshooting steps:

1. **Nếu vẫn có device error**:

   - Chạy CPU mode: `test_tts_cpu.py`
   - Set `DEVICE = "cpu"` trong config

2. **Nếu TTSnorm error**:

   - Code đã có fallback, sẽ dùng raw text

3. **Nếu memory error**:

   - Giảm batch size hoặc dùng CPU

4. **Nếu model loading error**:
   - Kiểm tra internet connection
   - Clear huggingface cache

## ✅ Expected result:

```
✅ Khởi tạo TTS Service thành công!
✅ Tìm thấy 1 giọng nói: gia_cat_luong
✅ Tạo thành công! File audio: temp_audio/gia_cat_luong_xxx.wav
```

**Service bây giờ sẽ hoạt động ổn định với device handling!**
