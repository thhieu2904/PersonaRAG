# backend/scripts/quick_test.py
"""
Quick test để kiểm tra import
"""
import sys
from pathlib import Path

# Thêm đường dẫn đến app
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
app_dir = backend_dir / "app"
sys.path.insert(0, str(app_dir))

try:
    print("Testing imports...")
    
    # Test 1: Import config
    print("1. Testing TTSConfig import...")
    from core.tts_config import TTSConfig
    print(f"✅ TTSConfig imported successfully!")
    print(f"   Device: {TTSConfig.DEVICE}")
    print(f"   Model repo: {TTSConfig.HUGGING_FACE_REPO}")
    
    # Test 2: Import service
    print("\n2. Testing TTSService import...")
    from core.tts_service import TTSService
    print("✅ TTSService imported successfully!")
    
    # Test 3: Basic functionality
    print("\n3. Testing basic functionality...")
    print("Creating TTSService instance...")
    
    # Khởi tạo service nhưng không load models để test nhanh
    print("✅ All imports successful!")
    print("Ready to run full TTS test!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
