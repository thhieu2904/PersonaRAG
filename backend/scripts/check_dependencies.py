#!/usr/bin/env python3
# backend/scripts/check_dependencies.py
"""
Script kiểm tra các dependencies cho TTS service
"""

import sys
import importlib

def check_import(module_name, package_name=None):
    """Kiểm tra xem module có thể import được không"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name or module_name}: OK")
        return True
    except ImportError as e:
        print(f"❌ {package_name or module_name}: FAILED - {e}")
        return False

def main():
    print("=" * 60)
    print("KIỂM TRA DEPENDENCIES CHO TTS SERVICE")
    print("=" * 60)
    
    # Danh sách dependencies cần kiểm tra
    dependencies = [
        ("torch", "PyTorch"),
        ("torchaudio", "TorchAudio"),
        ("soundfile", "SoundFile"),
        ("librosa", "Librosa"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("transformers", "Transformers"),
        ("accelerate", "Accelerate"),
        ("vocos", "Vocos"),
        ("pydub", "PyDub"),
        ("gradio", "Gradio"),
        ("click", "Click"),
        ("tqdm", "TQDM"),
        ("matplotlib", "Matplotlib"),
    ]
    
    # Dependencies có thể tùy chọn
    optional_dependencies = [
        ("vinorm", "ViNorm"),
        ("cached_path", "Cached Path"),
        ("huggingface_hub", "Hugging Face Hub"),
        ("x_transformers", "X-Transformers"),
        ("jieba", "Jieba"),
        ("pypinyin", "PyPinyin"),
        ("zhconv", "ZhConv"),
        ("zhon", "Zhon"),
        ("bitsandbytes", "BitsAndBytes"),
        ("pyaudio", "PyAudio"),
        ("faster_whisper", "Faster Whisper"),
        ("funasr", "FunASR"),
        ("jiwer", "JiWER"),
        ("modelscope", "ModelScope"),
    ]
    
    print("\n📦 CHECKING CORE DEPENDENCIES:")
    print("-" * 40)
    success_count = 0
    total_count = len(dependencies)
    
    for module, name in dependencies:
        if check_import(module, name):
            success_count += 1
    
    print(f"\n📊 Core Dependencies: {success_count}/{total_count} OK")
    
    print("\n🔧 CHECKING OPTIONAL DEPENDENCIES:")
    print("-" * 40)
    optional_success = 0
    optional_total = len(optional_dependencies)
    
    for module, name in optional_dependencies:
        if check_import(module, name):
            optional_success += 1
    
    print(f"\n📊 Optional Dependencies: {optional_success}/{optional_total} OK")
    
    # Kiểm tra PyTorch CUDA
    print("\n🔥 CHECKING PYTORCH CUDA:")
    print("-" * 40)
    try:
        import torch
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA version: {torch.version.cuda}")
            print(f"GPU count: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
    except Exception as e:
        print(f"❌ PyTorch CUDA check failed: {e}")
    
    print("\n" + "=" * 60)
    
    if success_count == total_count:
        print("🎉 TẤT CẢ CORE DEPENDENCIES ĐÃ SẴN SÀNG!")
        print("Bạn có thể chạy TTS service.")
    else:
        print("⚠️ CÓ MỘT SỐ DEPENDENCIES CHƯA ĐƯỢC CÀI ĐẶT")
        print("Hãy chạy: pip install -r requirements_tts.txt")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
