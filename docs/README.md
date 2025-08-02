# PersonaRAG Documentation

## 📚 Table of Contents

### 🚀 Setup & Deployment

- [Quick Start Guide](setup/quick-start.md) - Bắt đầu trong 5 phút
- [Local Deployment](setup/local-deployment.md) - Docker & development setup

### 🎤 Voice Management

- [Voice Settings Guide](voice/voice-settings.md) - Tùy chỉnh voice quality
- [Character Management](voice/character-management.md) - Thêm/xóa characters

### 👨‍💻 Development

- [Testing Guide](development/testing.md) - Test TTS service
- [API Reference](development/api-reference.md) - API endpoints
- [Architecture](development/architecture.md) - System design

### 🔧 Troubleshooting

- [Common Issues](troubleshooting/common-issues.md)
- [Performance Tuning](troubleshooting/performance.md)

## 🎯 Quick Links

### For Developers

```bash
# Quick test
cd backend && python test_tts_simple.py

# Configure voice
python scripts/configure_voice_settings.py preset --character gia_cat_luong

# Start development
docker-compose up -d
```

### For Users

- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## 📖 API Overview

### Generate Speech

```bash
curl -X POST "http://localhost:8000/api/v1/voice/generate-speech" \
     -H "Content-Type: application/json" \
     -d '{"text": "Xin chào", "character_name": "gia_cat_luong"}' \
     --output audio.wav
```

### List Characters

```bash
curl "http://localhost:8000/api/v1/voice/characters"
```

## 🔍 Project Structure

```
PersonaRAG/
├── docs/                    # 📚 Documentation
│   ├── setup/              # 🚀 Setup guides
│   ├── voice/              # 🎤 Voice management
│   ├── development/        # 👨‍💻 Dev guides
│   └── troubleshooting/    # 🔧 Problem solving
├── backend/                # 🐍 Python FastAPI
│   ├── app/core/           # TTS services
│   ├── data/voices/        # Character voice data
│   └── scripts/            # Management scripts
├── frontend/               # ⚛️ React UI
└── docker-compose.yml      # 🐳 Local deployment
```

## 🎭 Available Characters

Current characters with voice profiles:

- **gia_cat_luong** (Zhuge Liang) - Wise advisor
- **tu_ma_y** (Sima Yi) - Strategic general

## 🚀 Getting Started

1. **Quick Setup**: Follow [Quick Start Guide](setup/quick-start.md)
2. **Test Voice**: Run testing scripts
3. **Customize**: Configure voice settings
4. **Deploy**: Use Docker for local deployment

## 💡 Tips

- First run takes 1-2 minutes to download models
- Use voice presets for optimal quality
- Check logs for troubleshooting
- Docker setup recommended for consistent environment
