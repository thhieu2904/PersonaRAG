# backend/app/main_optimized.py
"""
FastAPI application với optimized TTS service
Sử dụng singleton pattern và async processing
"""
import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.tts_service_singleton import get_tts_service
from app.api.v1 import tts_optimized

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Preload models on startup
    """
    logger.info("🚀 Starting PersonaRAG TTS Service...")
    
    try:
        # Initialize singleton service (triggers model loading)
        service = get_tts_service()
        
        # Optional: Preload base model for faster first request
        # service._load_base_model()
        
        logger.info("✅ TTS Service startup completed")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    finally:
        logger.info("🛑 Shutting down TTS Service...")

# Create FastAPI app
app = FastAPI(
    title="PersonaRAG TTS Service",
    description="Optimized Text-to-Speech service with voice cloning and caching",
    version="2.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(tts_optimized.router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "PersonaRAG TTS Service",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "tts": "/api/v1/tts/synthesize",
            "tts_json": "/api/v1/tts/synthesize-json",
            "batch": "/api/v1/tts/synthesize-batch",
            "characters": "/api/v1/tts/characters",
            "stats": "/api/v1/tts/stats",
            "health": "/api/v1/tts/health"
        }
    }

@app.get("/health")
async def health():
    """Simple health check"""
    try:
        service = get_tts_service()
        health_status = service.health_check()
        return {
            "status": "healthy",
            "service_status": health_status["status"],
            "device": health_status["device"]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(
        "main_optimized:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload for production
        log_level="info"
    )
