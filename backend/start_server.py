# backend/start_server.py

"""
Script để khởi động server với đầy đủ tính năng
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if all dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required = [
        'fastapi', 'uvicorn', 'pydantic', 
        'chromadb', 'sentence_transformers'
    ]
    
    missing = []
    for pkg in required:
        try:
            __import__(pkg.replace('-', '_'))
            print(f"✅ {pkg}")
        except ImportError:
            missing.append(pkg)
            print(f"❌ {pkg}")
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("Install with: poetry install")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def setup_rag_if_needed():
    """Setup RAG system if not already done"""
    print("\n🧠 Checking RAG system...")
    
    db_path = Path("data/chroma_db")
    if not db_path.exists() or not list(db_path.glob("*")):
        print("📥 Setting up RAG system for first time...")
        try:
            result = subprocess.run([
                sys.executable, "scripts/setup_rag_system.py"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ RAG system setup completed!")
            else:
                print(f"⚠️  RAG setup had issues: {result.stderr}")
                print("Continuing with basic functionality...")
        except Exception as e:
            print(f"⚠️  Could not run RAG setup: {e}")
            print("Continuing with basic functionality...")
    else:
        print("✅ RAG system already initialized!")

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting PersonaRAG API Server...")
    print("=" * 50)
    print("📡 Server will be available at:")
    print("   - Main API: http://localhost:8000")
    print("   - API Docs: http://localhost:8000/docs")
    print("   - RAG API: http://localhost:8000/api/v1/rag/")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        subprocess.run([
            "uvicorn", "app.main:app", 
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Failed to start server: {e}")

def main():
    """Main function"""
    print("🏛️  PersonaRAG Server Startup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Setup RAG system
    setup_rag_if_needed()
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
