# Voice Settings Guide

## 🎛️ Voice Parameters

### Core Settings

| Parameter      | Range   | Default | Ảnh hưởng      |
| -------------- | ------- | ------- | -------------- |
| `speed`        | 0.5-2.0 | 0.8     | Tốc độ đọc     |
| `temperature`  | 0.1-1.0 | 0.7     | Biến đổi giọng |
| `pause_scale`  | 0.5-2.0 | 1.3     | Độ dài nghỉ    |
| `stress_scale` | 0.5-1.5 | 0.9     | Độ nhấn mạnh   |
| `pitch_scale`  | 0.8-1.2 | 1.0     | Cao độ giọng   |

### Vietnamese Optimization

```json
{
  "vietnamese_defaults": {
    "speed": 0.75,
    "pause_scale": 1.3,
    "stress_scale": 0.85,
    "temperature": 0.65
  }
}
```

## 🎭 Character Presets

### Gia Cát Lượng (Zhuge Liang)

**Personality**: Thông thái, chậm rãi, có uy tín

```json
{
  "speed": 0.75,
  "temperature": 0.65,
  "pause_scale": 1.4,
  "stress_scale": 0.85,
  "pitch_scale": 0.95
}
```

### Tư Mã Ý (Sima Yi)

**Personality**: Quyết đoán, nhanh nhẹn, năng động

```json
{
  "speed": 0.85,
  "temperature": 0.8,
  "pause_scale": 1.2,
  "stress_scale": 1.0,
  "pitch_scale": 1.05
}
```

## 🔧 Configuration Commands

### Xem danh sách characters

```bash
python scripts/configure_voice_settings.py list
```

### Xem settings hiện tại

```bash
python scripts/configure_voice_settings.py show --character gia_cat_luong
```

### Áp dụng preset

```bash
python scripts/configure_voice_settings.py preset --character gia_cat_luong
```

### Tùy chỉnh manual

```bash
python scripts/configure_voice_settings.py set \
    --character gia_cat_luong \
    --speed 0.7 \
    --temperature 0.6 \
    --pause_scale 1.5
```

## 📊 Quality Optimization

### Audio Sample Requirements

- **Format**: WAV, 24kHz, 16-bit
- **Duration**: 3-30 seconds per sample
- **Quality**: Clear, no background noise
- **Quantity**: 5-20 samples per character

### Common Issues & Solutions

1. **Giọng quá nhanh**:

   ```bash
   --speed 0.6 --pause_scale 1.5
   ```

2. **Giọng không tự nhiên**:

   ```bash
   --temperature 0.6 --stress_scale 0.8
   ```

3. **Nghỉ quá ngắn**:
   ```bash
   --pause_scale 1.4
   ```

## 🎯 Fine-tuning Tips

### For Formal Characters (Advisors)

- Lower speed (0.7-0.8)
- Higher pause_scale (1.3-1.5)
- Lower stress_scale (0.8-0.9)

### For Dynamic Characters (Warriors)

- Higher speed (0.85-0.95)
- Normal pause_scale (1.0-1.2)
- Higher stress_scale (1.0-1.2)

### Vietnamese-specific

- Always use pause_scale >= 1.2
- Keep temperature <= 0.8 for stability
- Lower pitch_scale for authority (0.9-0.95)
