# backend/simple_chat_test.py

"""
Simple chat test - Test nhanh chat AI trước khi chạy full test
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

def test_imports():
    """Test if all required packages are installed"""
    print("🔍 Testing imports...")
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        return False
    
    try:
        import llama_cpp
        print(f"✅ llama-cpp-python")
    except ImportError as e:
        print(f"❌ llama-cpp-python import failed: {e}")
        print("   Run: pip install llama-cpp-python")
        return False
    
    try:
        from huggingface_hub import hf_hub_download
        print(f"✅ huggingface_hub")
    except ImportError as e:
        print(f"❌ huggingface_hub import failed: {e}")
        print("   Run: pip install huggingface_hub")
        return False
    
    try:
        from app.core.ai_models import ChatAI, ModelConfig
        print(f"✅ Custom ChatAI module")
    except ImportError as e:
        print(f"❌ ChatAI import failed: {e}")
        return False
    
    return True

def test_model_download():
    """Test model download functionality"""
    print("\n📥 Testing model download...")
    
    from huggingface_hub import hf_hub_download
    
    try:
        # Test connection to HuggingFace
        model_name = "gaianet/Qwen2.5-7B-Instruct-GGUF"
        print(f"   Checking model: {model_name}")
        
        # Just check if we can access the repo (don't download yet)
        from huggingface_hub import list_repo_files
        files = list_repo_files(model_name)
        gguf_files = [f for f in files if f.endswith('.gguf')]
        
        print(f"   Found {len(gguf_files)} GGUF files:")
        for f in gguf_files[:5]:  # Show first 5
            print(f"     - {f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model download test failed: {e}")
        return False

def test_basic_functionality():
    """Test basic chat functionality without full model loading"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        from app.core.ai_models import ChatAI, ModelConfig
        
        # Create config but don't load model yet
        config = ModelConfig(
            model_name="gaianet/Qwen2.5-7B-Instruct-GGUF",
            model_file="qwen2.5-7b-instruct-q4_k_m.gguf",
            context_length=2048,  # Smaller for test
            max_tokens=256,
            n_gpu_layers=20,
            verbose=False
        )
        
        chat_ai = ChatAI(config)
        print("✅ ChatAI instance created")
        
        # Test configuration
        info = chat_ai.get_model_info()
        print(f"✅ Model info: {info['model_name']}")
        print(f"   Model loaded: {info['is_loaded']}")
        
        # Test history management
        chat_ai.clear_history()
        history = chat_ai.get_history()
        print(f"✅ History management works (length: {len(history)})")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def interactive_test():
    """Interactive test with user input"""
    print("\n💬 Interactive test (optional)")
    
    response = input("Do you want to test model loading and chat? (y/N): ").strip().lower()
    if response != 'y':
        print("Skipping interactive test")
        return True
    
    try:
        from app.core.ai_models import ChatAI, ModelConfig
        
        print("\n🔄 Loading model (this may take a few minutes)...")
        
        config = ModelConfig(
            model_name="gaianet/Qwen2.5-7B-Instruct-GGUF",
            model_file="Qwen2.5-7B-Instruct-Q4_K_M.gguf",
            context_length=2048,
            max_tokens=128,
            temperature=0.7,
            n_gpu_layers=15,  # Conservative for 6GB VRAM
            verbose=True
        )
        
        chat_ai = ChatAI(config)
        
        # Load model
        if not chat_ai.load_model():
            print("❌ Failed to load model")
            return False
        
        print("✅ Model loaded successfully!")
        
        # Simple test
        print("\n🤖 Testing chat...")
        response = chat_ai.chat("Xin chào! Bạn có biết Gia Cát Lượng không?")
        print(f"AI Response: {response}")
        
        # Cleanup
        chat_ai.unload_model()
        print("✅ Model unloaded")
        
        return True
        
    except Exception as e:
        print(f"❌ Interactive test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Simple Chat AI Test")
    print("=" * 50)
    
    # Test 1: Imports
    if not test_imports():
        print("\n❌ Import test failed. Please install missing dependencies.")
        return
    
    # Test 2: Model download
    if not test_model_download():
        print("\n❌ Model download test failed. Check internet connection.")
        return
    
    # Test 3: Basic functionality
    if not test_basic_functionality():
        print("\n❌ Basic functionality test failed.")
        return
    
    # Test 4: Interactive test (optional)
    interactive_test()
    
    print("\n" + "=" * 50)
    print("🎉 Simple tests completed!")
    print("\nNext steps:")
    print("1. Run full test: python test_chat_ai.py")
    print("2. Start API server: uvicorn app.main:app --reload")
    print("3. Test API at: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
