# backend/app/api/v1/tts_optimized.py
"""
Optimized TTS API endpoints cho production frontend
Sử dụng singleton service với caching và async support
"""
import asyncio
import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import Response
from pydantic import BaseModel, Field
import time

from ...core.tts_service_singleton import get_tts_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tts", tags=["TTS Optimized"])

# Request/Response models
class TTSRequest(BaseModel):
    """TTS synthesis request"""
    text: str = Field(..., min_length=1, max_length=1000, description="Text to synthesize")
    character: str = Field(default="gia_cat_luong", description="Character voice to use")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed multiplier")
    temperature: float = Field(default=0.7, ge=0.1, le=1.0, description="Voice variation")
    use_cache: bool = Field(default=True, description="Use audio cache if available")

class TTSBatchRequest(BaseModel):
    """Batch TTS synthesis request"""
    requests: List[TTSRequest] = Field(..., max_items=10, description="Batch of TTS requests")
    parallel: bool = Field(default=True, description="Process requests in parallel")

class TTSResponse(BaseModel):
    """TTS synthesis response"""
    success: bool
    message: str
    audio_length_seconds: Optional[float] = None
    inference_time_seconds: Optional[float] = None
    cache_hit: Optional[bool] = None
    character_used: Optional[str] = None

class ServiceStats(BaseModel):
    """Service statistics"""
    uptime_seconds: float
    total_requests: int
    cache_hits: int
    cache_hit_rate_percent: float
    average_inference_time: float
    cached_models: int
    cached_audio_files: int
    device: str
    base_model_loaded: bool

class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    device: str
    uptime: Optional[float] = None
    message: Optional[str] = None

# Dependency injection
async def get_service():
    """Dependency to get TTS service"""
    return get_tts_service()

@router.post("/synthesize", response_model=TTSResponse)
async def synthesize_speech(
    request: TTSRequest,
    background_tasks: BackgroundTasks,
    service = Depends(get_service)
) -> TTSResponse:
    """
    Synthesize speech từ text với character voice
    """
    start_time = time.time()
    
    try:
        logger.info(f"🎤 TTS request: {request.character} - {request.text[:50]}...")
        
        # Validate character
        available_chars = service.get_available_characters()
        if request.character not in available_chars:
            logger.warning(f"⚠️ Character '{request.character}' not found, using default")
            request.character = "gia_cat_luong"
        
        # Synthesize speech
        audio_bytes = await service.synthesize_speech_async(
            text=request.text,
            character=request.character,
            speed=request.speed,
            temperature=request.temperature
        )
        
        # Calculate audio length
        import io
        import soundfile as sf
        
        buffer = io.BytesIO(audio_bytes)
        data, sample_rate = sf.read(buffer)
        audio_length = len(data) / sample_rate
        
        inference_time = time.time() - start_time
        
        # Log performance metrics in background
        background_tasks.add_task(
            log_performance_metrics,
            request.character,
            len(request.text),
            inference_time,
            audio_length
        )
        
        # Return audio as response
        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "X-Audio-Length": str(audio_length),
                "X-Inference-Time": str(inference_time),
                "X-Character": request.character,
                "X-Cache-Hit": "false"  # TODO: Implement cache hit detection
            }
        )
        
    except Exception as e:
        logger.error(f"❌ TTS synthesis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"TTS synthesis failed: {str(e)}"
        )

@router.post("/synthesize-json", response_model=TTSResponse)
async def synthesize_speech_json(
    request: TTSRequest,
    background_tasks: BackgroundTasks,
    service = Depends(get_service)
) -> TTSResponse:
    """
    Synthesize speech và return JSON response với base64 audio
    """
    start_time = time.time()
    
    try:
        logger.info(f"🎤 TTS JSON request: {request.character} - {request.text[:50]}...")
        
        # Validate character
        available_chars = service.get_available_characters()
        if request.character not in available_chars:
            logger.warning(f"⚠️ Character '{request.character}' not found, using default")
            request.character = "gia_cat_luong"
        
        # Synthesize speech
        audio_bytes = await service.synthesize_speech_async(
            text=request.text,
            character=request.character,
            speed=request.speed,
            temperature=request.temperature
        )
        
        # Calculate audio length
        import io
        import soundfile as sf
        import base64
        
        buffer = io.BytesIO(audio_bytes)
        data, sample_rate = sf.read(buffer)
        audio_length = len(data) / sample_rate
        
        inference_time = time.time() - start_time
        
        # Encode audio to base64
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        # Log performance metrics in background
        background_tasks.add_task(
            log_performance_metrics,
            request.character,
            len(request.text),
            inference_time,
            audio_length
        )
        
        return {
            "success": True,
            "message": "Synthesis completed successfully",
            "audio_base64": audio_b64,
            "audio_length_seconds": audio_length,
            "inference_time_seconds": inference_time,
            "cache_hit": False,  # TODO: Implement cache hit detection
            "character_used": request.character
        }
        
    except Exception as e:
        logger.error(f"❌ TTS synthesis failed: {e}")
        return {
            "success": False,
            "message": f"TTS synthesis failed: {str(e)}",
            "audio_base64": None,
            "audio_length_seconds": None,
            "inference_time_seconds": time.time() - start_time,
            "cache_hit": False,
            "character_used": request.character
        }

@router.post("/synthesize-batch")
async def synthesize_batch(
    request: TTSBatchRequest,
    background_tasks: BackgroundTasks,
    service = Depends(get_service)
):
    """
    Batch synthesis cho multiple requests
    """
    start_time = time.time()
    results = []
    
    try:
        logger.info(f"🎤 Batch TTS request: {len(request.requests)} items")
        
        if request.parallel:
            # Process in parallel
            tasks = [
                service.synthesize_speech_async(
                    text=req.text,
                    character=req.character,
                    speed=req.speed,
                    temperature=req.temperature
                )
                for req in request.requests
            ]
            
            audio_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, (req, audio_result) in enumerate(zip(request.requests, audio_results)):
                if isinstance(audio_result, Exception):
                    results.append({
                        "index": i,
                        "success": False,
                        "message": str(audio_result),
                        "character": req.character
                    })
                else:
                    import base64
                    results.append({
                        "index": i,
                        "success": True,
                        "message": "Success",
                        "audio_base64": base64.b64encode(audio_result).decode('utf-8'),
                        "character": req.character
                    })
        else:
            # Process sequentially
            for i, req in enumerate(request.requests):
                try:
                    audio_bytes = await service.synthesize_speech_async(
                        text=req.text,
                        character=req.character,
                        speed=req.speed,
                        temperature=req.temperature
                    )
                    
                    import base64
                    results.append({
                        "index": i,
                        "success": True,
                        "message": "Success",
                        "audio_base64": base64.b64encode(audio_bytes).decode('utf-8'),
                        "character": req.character
                    })
                    
                except Exception as e:
                    results.append({
                        "index": i,
                        "success": False,
                        "message": str(e),
                        "character": req.character
                    })
        
        total_time = time.time() - start_time
        
        # Log batch performance
        background_tasks.add_task(
            log_batch_performance,
            len(request.requests),
            total_time,
            request.parallel
        )
        
        return {
            "success": True,
            "message": f"Batch processing completed",
            "total_requests": len(request.requests),
            "successful_requests": sum(1 for r in results if r["success"]),
            "total_time_seconds": total_time,
            "parallel_processing": request.parallel,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Batch TTS failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch TTS failed: {str(e)}"
        )

@router.get("/characters")
async def get_available_characters(service = Depends(get_service)) -> Dict[str, List[str]]:
    """
    Get list of available character voices
    """
    try:
        characters = service.get_available_characters()
        
        return {
            "success": True,
            "characters": characters,
            "total_count": len(characters)
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get characters: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get characters: {str(e)}"
        )

@router.get("/stats", response_model=ServiceStats)
async def get_service_stats(service = Depends(get_service)) -> ServiceStats:
    """
    Get service performance statistics
    """
    try:
        stats = service.get_stats()
        return ServiceStats(**stats)
        
    except Exception as e:
        logger.error(f"❌ Failed to get stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats: {str(e)}"
        )

@router.get("/health", response_model=HealthCheck)
async def health_check(service = Depends(get_service)) -> HealthCheck:
    """
    Service health check
    """
    try:
        health = service.health_check()
        return HealthCheck(**health)
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return HealthCheck(
            status="error",
            device="unknown",
            message=str(e)
        )

@router.delete("/cache")
async def clear_cache(
    cache_type: str = "all",
    service = Depends(get_service)
) -> Dict[str, str]:
    """
    Clear service caches
    """
    try:
        if cache_type not in ["all", "audio", "models", "stats"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid cache type. Use: all, audio, models, or stats"
            )
        
        service.clear_cache(cache_type)
        
        return {
            "success": True,
            "message": f"Cache '{cache_type}' cleared successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to clear cache: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )

# Background task functions
async def log_performance_metrics(
    character: str,
    text_length: int,
    inference_time: float,
    audio_length: float
):
    """Log performance metrics in background"""
    logger.info(
        f"📊 Performance - Character: {character}, "
        f"Text length: {text_length}, "
        f"Inference time: {inference_time:.2f}s, "
        f"Audio length: {audio_length:.2f}s"
    )

async def log_batch_performance(
    batch_size: int,
    total_time: float,
    parallel: bool
):
    """Log batch performance metrics"""
    avg_time = total_time / batch_size if batch_size > 0 else 0
    logger.info(
        f"📊 Batch Performance - Size: {batch_size}, "
        f"Total time: {total_time:.2f}s, "
        f"Avg time: {avg_time:.2f}s, "
        f"Parallel: {parallel}"
    )
