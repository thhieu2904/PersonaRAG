# backend/app/api/v1/chat_ai.py

"""
Chat AI API endpoints
Cung cấp REST API cho hệ thống chat AI
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import json
import asyncio
from datetime import datetime

from app.core.ai_models import get_chat_ai, ChatAI, ModelConfig, create_custom_chat_ai

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    system_prompt: Optional[str] = Field(None, description="System prompt to set context")
    reset_history: bool = Field(False, description="Reset conversation history")
    stream: bool = Field(False, description="Enable streaming response")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI response")
    timestamp: datetime = Field(default_factory=datetime.now)
    model_info: Dict[str, Any] = Field(..., description="Model information")

class ConfigRequest(BaseModel):
    model_name: Optional[str] = Field("gaianet/Qwen2.5-7B-Instruct-GGUF", description="Model repository name")
    model_file: Optional[str] = Field("qwen2.5-7b-instruct-q4_k_m.gguf", description="Model file name")
    context_length: Optional[int] = Field(4096, description="Context length")
    max_tokens: Optional[int] = Field(512, description="Maximum tokens per response")
    temperature: Optional[float] = Field(0.7, description="Temperature for randomness")
    top_p: Optional[float] = Field(0.95, description="Top-p sampling")
    top_k: Optional[int] = Field(40, description="Top-k sampling")
    n_gpu_layers: Optional[int] = Field(25, description="Number of GPU layers")
    n_threads: Optional[int] = Field(8, description="Number of CPU threads")

class HistoryResponse(BaseModel):
    history: List[Dict[str, Any]] = Field(..., description="Conversation history")
    total_messages: int = Field(..., description="Total number of messages")

class ModelInfoResponse(BaseModel):
    model_name: str
    model_file: str
    is_loaded: bool
    context_length: int
    max_tokens: int
    n_gpu_layers: int
    conversation_length: int

# Global chat AI instance
current_chat_ai: Optional[ChatAI] = None

def get_current_chat_ai() -> ChatAI:
    """Get current chat AI instance"""
    global current_chat_ai
    if current_chat_ai is None:
        current_chat_ai = get_chat_ai()
    return current_chat_ai

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Chat with AI model
    
    - **message**: Your message to the AI
    - **system_prompt**: Optional system prompt to set context
    - **reset_history**: Whether to reset conversation history
    - **stream**: Whether to stream the response (not applicable for this endpoint)
    """
    try:
        chat_ai = get_current_chat_ai()
        
        # Generate response
        response = chat_ai.chat(
            user_message=request.message,
            system_prompt=request.system_prompt,
            reset_history=request.reset_history
        )
        
        # Get model info
        model_info = chat_ai.get_model_info()
        
        return ChatResponse(
            response=response,
            model_info=model_info
        )
        
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat generation failed: {str(e)}")

@router.post("/chat/stream")
async def chat_stream_with_ai(request: ChatRequest):
    """
    Stream chat with AI model
    
    Returns a streaming response with Server-Sent Events (SSE) format
    """
    try:
        chat_ai = get_current_chat_ai()
        
        async def generate_stream():
            try:
                # Send initial event
                yield f"data: {json.dumps({'type': 'start', 'message': 'Starting response generation...'})}\n\n"
                
                # Generate streaming response
                full_response = ""
                for token in chat_ai.chat_stream(
                    user_message=request.message,
                    system_prompt=request.system_prompt,
                    reset_history=request.reset_history
                ):
                    full_response += token
                    yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                    await asyncio.sleep(0.01)  # Small delay for better UX
                
                # Send completion event
                model_info = chat_ai.get_model_info()
                yield f"data: {json.dumps({'type': 'complete', 'full_response': full_response, 'model_info': model_info})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
        
    except Exception as e:
        logger.error(f"Stream chat API error: {e}")
        raise HTTPException(status_code=500, detail=f"Stream chat generation failed: {str(e)}")

@router.get("/history", response_model=HistoryResponse)
async def get_conversation_history():
    """Get conversation history"""
    try:
        chat_ai = get_current_chat_ai()
        history = chat_ai.get_history()
        
        return HistoryResponse(
            history=history,
            total_messages=len(history)
        )
        
    except Exception as e:
        logger.error(f"Get history API error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@router.delete("/history")
async def clear_conversation_history():
    """Clear conversation history"""
    try:
        chat_ai = get_current_chat_ai()
        chat_ai.clear_history()
        
        return {"message": "Conversation history cleared successfully"}
        
    except Exception as e:
        logger.error(f"Clear history API error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear history: {str(e)}")

@router.get("/model/info", response_model=ModelInfoResponse)
async def get_model_info():
    """Get current model information"""
    try:
        chat_ai = get_current_chat_ai()
        model_info = chat_ai.get_model_info()
        
        return ModelInfoResponse(**model_info)
        
    except Exception as e:
        logger.error(f"Get model info API error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")

@router.post("/model/load")
async def load_model():
    """Load the AI model"""
    try:
        chat_ai = get_current_chat_ai()
        success = chat_ai.load_model()
        
        if success:
            model_info = chat_ai.get_model_info()
            return {"message": "Model loaded successfully", "model_info": model_info}
        else:
            raise HTTPException(status_code=500, detail="Failed to load model")
            
    except Exception as e:
        logger.error(f"Load model API error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")

@router.post("/model/unload")
async def unload_model():
    """Unload the AI model to free memory"""
    try:
        chat_ai = get_current_chat_ai()
        chat_ai.unload_model()
        
        return {"message": "Model unloaded successfully"}
        
    except Exception as e:
        logger.error(f"Unload model API error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to unload model: {str(e)}")

@router.post("/model/configure")
async def configure_model(config_request: ConfigRequest, background_tasks: BackgroundTasks):
    """
    Configure and reload model with new settings
    
    Note: This will unload the current model and load a new one with the specified configuration
    """
    try:
        global current_chat_ai
        
        # Create new configuration
        new_config = ModelConfig(
            model_name=config_request.model_name,
            model_file=config_request.model_file,
            context_length=config_request.context_length,
            max_tokens=config_request.max_tokens,
            temperature=config_request.temperature,
            top_p=config_request.top_p,
            top_k=config_request.top_k,
            n_gpu_layers=config_request.n_gpu_layers,
            n_threads=config_request.n_threads
        )
        
        # Unload current model if exists
        if current_chat_ai:
            current_chat_ai.unload_model()
        
        # Create new chat AI instance
        current_chat_ai = create_custom_chat_ai(new_config)
        
        # Load model in background
        def load_in_background():
            try:
                current_chat_ai.load_model()
                logger.info("Model loaded successfully with new configuration")
            except Exception as e:
                logger.error(f"Failed to load model with new config: {e}")
        
        background_tasks.add_task(load_in_background)
        
        return {
            "message": "Model configuration updated. Loading in background...",
            "config": new_config.__dict__
        }
        
    except Exception as e:
        logger.error(f"Configure model API error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to configure model: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        chat_ai = get_current_chat_ai()
        model_info = chat_ai.get_model_info()
        
        return {
            "status": "healthy",
            "model_loaded": model_info["is_loaded"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
