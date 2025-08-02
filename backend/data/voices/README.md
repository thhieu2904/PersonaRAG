# Data Structure cho Few-Shot Voice Training

## 📁 Cấu trúc thư mục:

```
backend/
├── data/
│   └── voices/                    # 🎯 Few-shot training data
│       ├── gia_cat_luong/
│       │   ├── sample_01.wav      # Audio samples (3-15s mỗi file)
│       │   ├── sample_02.wav
│       │   ├── sample_03.wav
│       │   └── metadata.json      # Thông tin về character
│       ├── lu_bo/
│       │   ├── sample_01.wav
│       │   └── metadata.json
│       └── cao_cao/
│           ├── sample_01.wav
│           └── metadata.json
├── models/
│   └── tuned_models/              # 🎯 Output của fine-tuning
│       ├── gia_cat_luong.pt
│       ├── lu_bo.pt
│       └── cao_cao.pt
└── audio_samples/                 # 🔄 Legacy (sẽ migrate)
    └── gia_cat_luong.wav
```

## 📋 Yêu cầu cho mỗi character:

### Audio samples:

- **Số lượng**: 3-10 files
- **Độ dài**: 3-15 giây mỗi file
- **Chất lượng**: 24kHz, mono, ít noise
- **Nội dung**: Đa dạng câu, tránh lặp lại

### Metadata.json:

```json
{
  "character_name": "gia_cat_luong",
  "description": "Quân sư thông minh, giọng điềm tĩnh",
  "language": "vi",
  "sample_rate": 24000,
  "samples": [
    {
      "file": "sample_01.wav",
      "text": "Văn bản tương ứng với audio",
      "duration": 5.2
    }
  ],
  "tuning_config": {
    "learning_rate": 1e-5,
    "epochs": 50,
    "batch_size": 2
  }
}
```

## 🔄 Migration plan:

1. Copy `gia_cat_luong.wav` → `data/voices/gia_cat_luong/sample_01.wav`
2. Tạo metadata.json cho character này
3. Thêm thêm samples nếu có
