#!/bin/bash
# backend/scripts/setup_environment.sh
echo "======================================================"
echo "THIẾT LẬP MÔI TRƯỜNG CHO PERSONA RAG TTS"
echo "======================================================"

echo ""
echo "1. Cài đặt dependencies với Poetry..."
cd "$(dirname "$0")/.."
poetry install

echo ""
echo "2. Kiểm tra cài đặt PyTorch CUDA..."
poetry run python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"

echo ""
echo "3. Kiểm tra F5-TTS dependencies..."
poetry run python -c "
try:
    import soundfile as sf
    print('✅ soundfile OK')
except ImportError as e:
    print(f'❌ soundfile: {e}')

try:
    import vinorm
    print('✅ vinorm OK')
except ImportError as e:
    print(f'❌ vinorm: {e}')

try:
    from cached_path import cached_path
    print('✅ cached_path OK')
except ImportError as e:
    print(f'❌ cached_path: {e}')

try:
    import vocos
    print('✅ vocos OK')
except ImportError as e:
    print(f'❌ vocos: {e}')
"

echo ""
echo "4. Tạo thư mục cần thiết..."
mkdir -p temp_audio
mkdir -p data/audio_samples
mkdir -p data/knowledge_base
mkdir -p models/voice_profiles

echo ""
echo "======================================================"
echo "HOÀN THÀNH THIẾT LẬP MÔI TRƯỜNG"
echo "======================================================"
echo ""
echo "Để test TTS service, chạy:"
echo "poetry run python scripts/test_tts_service.py"
