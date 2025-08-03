@echo off
REM Setup script for PersonaRAG LLM features on Windows
REM Optimized for RTX 3060 6GB VRAM

echo ========================================
echo PersonaRAG LLM Setup Script
echo RTX 3060 6GB VRAM Configuration
echo ========================================

echo.
echo Checking system requirements...

REM Check if CUDA is available
nvidia-smi >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: NVIDIA GPU not detected or drivers not installed
    echo Please install NVIDIA drivers and CUDA toolkit first
    pause
    exit /b 1
)

echo ✅ NVIDIA GPU detected

REM Check if Poetry is installed
poetry --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Poetry not found. Please install Poetry first:
    echo curl -sSL https://install.python-poetry.org | python3 -
    pause
    exit /b 1
)

echo ✅ Poetry detected

echo.
echo Installing dependencies...

REM Install main dependencies
echo Installing main dependencies with Poetry...
poetry install

REM Install additional packages for LLM fine-tuning
echo.
echo Installing additional packages...

REM PEFT for LoRA fine-tuning
poetry add peft

REM BitsAndBytesConfig for quantization
poetry add bitsandbytes

REM Additional dependencies for model handling
poetry add accelerate>=0.33.0
poetry add transformers>=4.36.0

REM Monitoring tools
poetry add psutil

REM Optional: Weights & Biases for training monitoring
poetry add wandb --optional

echo.
echo ========================================
echo Installation completed!
echo ========================================

echo.
echo Next steps:
echo 1. Test the basic chat model:
echo    poetry run python test_qwen_chat.py
echo.
echo 2. Test interactive chat:
echo    poetry run python test_qwen_chat.py --interactive
echo.
echo 3. Test fine-tuning preparation:
echo    poetry run python test_qwen_chat.py --test-finetuning
echo.

echo System Configuration:
echo - Model: Qwen2.5-7B-Instruct (4-bit quantized)
echo - Max sequence length: 2048 tokens
echo - Optimized for 6GB VRAM
echo - LoRA fine-tuning ready

echo.
echo Press any key to exit...
pause >nul
