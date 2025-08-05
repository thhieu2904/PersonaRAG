# backend/app/core/ai_models.py

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Iterator
from dataclasses import dataclass
import time

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    Llama = None

from huggingface_hub import hf_hub_download
import threading
from .enhanced_config import create_optimized_model_config

logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Represents a chat message"""
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: Optional[float] = None

@dataclass
class ModelConfig:
    """Configuration for AI model - Optimized for RTX 3060 6GB"""
    model_name: str = "gaianet/Qwen2.5-7B-Instruct-GGUF"
    model_file: str = "Qwen2.5-7B-Instruct-Q4_K_M.gguf"
    context_length: int = 3072  # Reduced for stability with RAG contexts
    max_tokens: int = 400  # Optimized for character responses
    temperature: float = 0.8
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.15
    n_gpu_layers: int = 25  # Optimized for RTX 3060 6GB
    n_threads: int = 8
    use_mmap: bool = True
    use_mlock: bool = False
    verbose: bool = False

class ChatAI:
    """Main Chat AI class using GGUF models"""
    
    def __init__(self, config: Optional[ModelConfig] = None):
        # Sử dụng enhanced config nếu không có config được cung cấp
        if config is None:
            enhanced_config = create_optimized_model_config()
            self.config = ModelConfig(**enhanced_config)
        else:
            self.config = config
            
        self.model = None  # Type: Optional[Llama]
        self.is_loaded = False
        self.conversation_history: List[ChatMessage] = []
        self._lock = threading.Lock()
        
        # Thiết lập thư mục models
        self.models_dir = Path(__file__).resolve().parent.parent.parent / "models" / "chat"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ChatAI initialized with config: {self.config}")
    
    def _download_model(self) -> str:
        """Download model from HuggingFace if not exists"""
        model_path = self.models_dir / self.config.model_file
        
        if model_path.exists():
            logger.info(f"Model already exists at: {model_path}")
            return str(model_path)
        
        logger.info(f"Downloading model {self.config.model_name}/{self.config.model_file}...")
        try:
            downloaded_path = hf_hub_download(
                repo_id=self.config.model_name,
                filename=self.config.model_file,
                local_dir=str(self.models_dir),
                local_dir_use_symlinks=False
            )
            logger.info(f"Model downloaded successfully to: {downloaded_path}")
            return downloaded_path
        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            raise
    
    def load_model(self) -> bool:
        """Load the GGUF model"""
        if not LLAMA_CPP_AVAILABLE:
            logger.error("llama-cpp-python is not installed. Please install it: pip install llama-cpp-python")
            return False
        
        with self._lock:
            if self.is_loaded:
                logger.info("Model already loaded")
                return True
            
            try:
                # Download model if needed
                model_path = self._download_model()
                
                logger.info("Loading GGUF model...")
                self.model = Llama(
                    model_path=model_path,
                    n_ctx=self.config.context_length,
                    n_gpu_layers=self.config.n_gpu_layers,
                    n_threads=self.config.n_threads,
                    use_mmap=self.config.use_mmap,
                    use_mlock=self.config.use_mlock,
                    verbose=self.config.verbose
                )
                
                self.is_loaded = True
                logger.info("Model loaded successfully!")
                return True
                
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                return False
    
    def _format_conversation(self, messages: List[ChatMessage]) -> str:
        """Format conversation for Qwen2.5 ChatML template"""
        formatted = ""
        
        for msg in messages:
            if msg.role == "system":
                formatted += f"<|im_start|>system\n{msg.content}<|im_end|>\n"
            elif msg.role == "user":
                formatted += f"<|im_start|>user\n{msg.content}<|im_end|>\n"
            elif msg.role == "assistant":
                formatted += f"<|im_start|>assistant\n{msg.content}<|im_end|>\n"
        
        # Add assistant start token for next response
        formatted += "<|im_start|>assistant\n"
        return formatted
    
    def chat(self, 
             user_message: str, 
             system_prompt: Optional[str] = None,
             reset_history: bool = False) -> str:
        """Chat with the AI model"""
        
        if not self.is_loaded:
            if not self.load_model():
                return "Lỗi: Không thể tải model AI. Vui lòng kiểm tra cấu hình."
        
        try:
            with self._lock:
                # Reset conversation if requested
                if reset_history:
                    self.conversation_history.clear()
                
                # Add system prompt if provided and not already in history
                if system_prompt and (not self.conversation_history or 
                                    self.conversation_history[0].role != "system"):
                    if self.conversation_history:
                        # Insert at beginning
                        self.conversation_history.insert(0, ChatMessage("system", system_prompt, time.time()))
                    else:
                        self.conversation_history.append(ChatMessage("system", system_prompt, time.time()))
                
                # Add user message
                self.conversation_history.append(ChatMessage("user", user_message, time.time()))
                
                # Format conversation
                prompt = self._format_conversation(self.conversation_history)
                
                # Check prompt length to avoid context overflow
                if len(prompt) > self.config.context_length * 3:  # Rough token estimate
                    logger.warning(f"Prompt too long ({len(prompt)} chars), truncating history")
                    # Keep only system prompt + last 2 exchanges
                    recent_history = []
                    if self.conversation_history[0].role == "system":
                        recent_history.append(self.conversation_history[0])
                    recent_history.extend(self.conversation_history[-3:])  # Last user + assistant + current user
                    self.conversation_history = recent_history
                    prompt = self._format_conversation(self.conversation_history)
                
                logger.info(f"Sending prompt to model (length: {len(prompt)} chars)")
                
                # Generate response
                response = self.model.create_completion(
                    prompt=prompt,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    top_p=self.config.top_p,
                    top_k=self.config.top_k,
                    repeat_penalty=self.config.repeat_penalty,
                    stop=["<|im_end|>", "<|im_start|>"],
                    stream=False
                )
                
                assistant_message = response['choices'][0]['text'].strip()
                
                # Add assistant response to history
                self.conversation_history.append(ChatMessage("assistant", assistant_message, time.time()))
                
                logger.info(f"Generated response (length: {len(assistant_message)} chars)")
                return assistant_message
                
        except Exception as e:
            logger.error(f"Chat generation failed: {e}")
            return f"Lỗi khi tạo phản hồi: {str(e)}"
    
    def chat_stream(self, 
                   user_message: str, 
                   system_prompt: Optional[str] = None,
                   reset_history: bool = False) -> Iterator[str]:
        """Stream chat response"""
        
        if not self.is_loaded:
            if not self.load_model():
                yield "Lỗi: Không thể tải model AI. Vui lòng kiểm tra cấu hình."
                return
        
        try:
            with self._lock:
                # Reset conversation if requested
                if reset_history:
                    self.conversation_history.clear()
                
                # Add system prompt if provided
                if system_prompt and (not self.conversation_history or 
                                    self.conversation_history[0].role != "system"):
                    if self.conversation_history:
                        self.conversation_history.insert(0, ChatMessage("system", system_prompt, time.time()))
                    else:
                        self.conversation_history.append(ChatMessage("system", system_prompt, time.time()))
                
                # Add user message
                self.conversation_history.append(ChatMessage("user", user_message, time.time()))
                
                # Format conversation
                prompt = self._format_conversation(self.conversation_history)
                
                logger.info(f"Streaming response for prompt (length: {len(prompt)} chars)")
                
                # Generate streaming response
                response_stream = self.model.create_completion(
                    prompt=prompt,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    top_p=self.config.top_p,
                    top_k=self.config.top_k,
                    repeat_penalty=self.config.repeat_penalty,
                    stop=["<|im_end|>", "<|im_start|>"],
                    stream=True
                )
                
                full_response = ""
                for chunk in response_stream:
                    if chunk['choices'][0]['text']:
                        token = chunk['choices'][0]['text']
                        full_response += token
                        yield token
                
                # Add complete assistant response to history
                self.conversation_history.append(ChatMessage("assistant", full_response.strip(), time.time()))
                
        except Exception as e:
            logger.error(f"Stream chat generation failed: {e}")
            yield f"Lỗi khi tạo phản hồi: {str(e)}"
    
    def clear_history(self):
        """Clear conversation history"""
        with self._lock:
            self.conversation_history.clear()
            logger.info("Conversation history cleared")
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp
            }
            for msg in self.conversation_history
        ]
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": self.config.model_name,
            "model_file": self.config.model_file,
            "is_loaded": self.is_loaded,
            "context_length": self.config.context_length,
            "max_tokens": self.config.max_tokens,
            "n_gpu_layers": self.config.n_gpu_layers,
            "conversation_length": len(self.conversation_history)
        }
    
    def unload_model(self):
        """Unload model to free memory"""
        with self._lock:
            if self.model:
                del self.model
                self.model = None
                self.is_loaded = False
                logger.info("Model unloaded")

# Singleton instance
_chat_ai_instance: Optional[ChatAI] = None

def get_chat_ai() -> ChatAI:
    """Get singleton ChatAI instance"""
    global _chat_ai_instance
    if _chat_ai_instance is None:
        _chat_ai_instance = ChatAI()
    return _chat_ai_instance

def create_custom_chat_ai(config: ModelConfig) -> ChatAI:
    """Create ChatAI instance with custom config"""
    return ChatAI(config)
