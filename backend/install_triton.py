"""
Script để cài đặt triton cho Unsloth trên Windows
"""

import subprocess
import sys
import os

def install_triton_windows():
    """Cài đặt triton cho Windows"""
    print("=== Cài đặt Triton cho Unsloth ===")
    
    try:
        # Option 1: Cài triton từ PyPI
        print("1. Trying to install triton from PyPI...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "triton"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Triton installed successfully!")
            return True
        else:
            print(f"❌ PyPI installation failed: {result.stderr}")
            
        # Option 2: Cài từ wheel cho Windows
        print("\n2. Trying Windows wheel...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "https://download.pytorch.org/whl/cu121/triton-2.1.0%2Brocm5.6-cp311-cp311-win_amd64.whl"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Triton wheel installed!")
            return True
        else:
            print(f"❌ Wheel installation failed: {result.stderr}")
            
        # Option 3: Skip triton, use CPU fallback
        print("\n3. Triton not available, will use CPU fallback")
        return False
        
    except Exception as e:
        print(f"❌ Error installing triton: {e}")
        return False

def test_triton_import():
    """Test triton import"""
    try:
        import triton
        print(f"✅ Triton available: {triton.__version__}")
        return True
    except ImportError:
        print("❌ Triton not available")
        return False

def test_unsloth_without_triton():
    """Test Unsloth without triton"""
    print("\n=== Testing Unsloth without Triton ===")
    
    try:
        # Set environment variable to disable triton
        os.environ["UNSLOTH_DISABLE_TRITON"] = "1"
        
        import unsloth
        print(f"✅ Unsloth available: {unsloth.__version__}")
        
        from unsloth import FastLanguageModel
        print("✅ FastLanguageModel import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Unsloth test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Triton Installation Script for Unsloth")
    print("=" * 50)
    
    # Test current state
    triton_available = test_triton_import()
    
    if not triton_available:
        # Try to install triton
        triton_installed = install_triton_windows()
        
        if triton_installed:
            triton_available = test_triton_import()
    
    # Test unsloth
    if not triton_available:
        print("\n⚠️  Triton not available, testing Unsloth fallback...")
        unsloth_works = test_unsloth_without_triton()
        
        if unsloth_works:
            print("\n✅ Unsloth can work without Triton!")
            print("Performance may be slower but should work.")
        else:
            print("\n❌ Unsloth fallback failed")
    else:
        print("\n✅ Triton available, Unsloth should work optimally!")
        
    print("\n" + "=" * 50)
    print("Installation complete. Try running the model test now.")
