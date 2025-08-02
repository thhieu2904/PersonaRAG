@echo off
:: backend/scripts/setup_environment.bat
echo ======================================================
echo THIẾT LẬP MÔI TRƯỜNG CHO PERSONA RAG TTS
echo ======================================================

echo.
echo 1. Cài đặt dependencies với Poetry...
cd /d "%~dp0\.."
poetry install

echo.
echo 2. Kiểm tra cài đặt PyTorch CUDA...
poetry run python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"

echo.
echo 3. Kiểm tra F5-TTS dependencies...
poetry run python -c "try:\n    import soundfile as sf\n    print('✅ soundfile OK')\nexcept ImportError as e:\n    print(f'❌ soundfile: {e}')\n\ntry:\n    import vinorm\n    print('✅ vinorm OK')\nexcept ImportError as e:\n    print(f'❌ vinorm: {e}')\n\ntry:\n    from cached_path import cached_path\n    print('✅ cached_path OK')\nexcept ImportError as e:\n    print(f'❌ cached_path: {e}')\n\ntry:\n    import vocos\n    print('✅ vocos OK')\nexcept ImportError as e:\n    print(f'❌ vocos: {e}')"

echo.
echo 4. Tạo thư mục cần thiết...
if not exist "temp_audio" mkdir temp_audio
if not exist "data\audio_samples" mkdir data\audio_samples
if not exist "data\knowledge_base" mkdir data\knowledge_base
if not exist "models\voice_profiles" mkdir models\voice_profiles

echo.
echo ======================================================
echo HOÀN THÀNH THIẾT LẬP MÔI TRƯỜNG
echo ======================================================
echo.
echo Để test TTS service, chạy:
echo poetry run python scripts/test_tts_service.py

pause
