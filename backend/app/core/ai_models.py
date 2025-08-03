"""
AI Models management for PersonaRAG
Integrates F5-TTS for voice synthesis and Qwen2.5 for chat capabilities
"""

from typing import Optional, Dict, Any
import logging
from .llm_chat import QwenChatModel

logger = logging.getLogger(__name__)

class AIModelsManager:
    """
    Centralized manager for all AI models in PersonaRAG
    """
    
    def __init__(self):
        self.tts_model = None
        self.chat_model: Optional[QwenChatModel] = None
        self._models_loaded = {
            "tts": False,
            "chat": False
        }
        
    def load_chat_model(self, 
                       model_name: str = "unsloth/Qwen2.5-7B-Instruct-unsloth-bnb-4bit",
                       max_seq_length: int = 2048,
                       load_in_4bit: bool = True) -> bool:
        """
        Load Qwen chat model
        
        Args:
            model_name: HuggingFace model name
            max_seq_length: Maximum sequence length
            load_in_4bit: Use 4-bit quantization
            
        Returns:
            Success status
        """
        try:
            logger.info("Loading Qwen chat model...")
            
            self.chat_model = QwenChatModel(
                model_name=model_name,
                max_seq_length=max_seq_length,
                load_in_4bit=load_in_4bit
            )
            
            self.chat_model.load_model()
            self._models_loaded["chat"] = True
            
            logger.info("Chat model loaded successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load chat model: {e}")
            return False
            
    def load_tts_model(self):
        """Load F5-TTS model (placeholder for now)"""
        # TODO: Implement F5-TTS loading
        logger.info("TTS model loading not implemented yet")
        pass
        
    def generate_chat_response(self, user_input: str, **kwargs) -> str:
        """
        Generate chat response using loaded model
        
        Args:
            user_input: User's message
            **kwargs: Additional generation parameters
            
        Returns:
            Generated response
        """
        if not self._models_loaded["chat"] or self.chat_model is None:
            raise RuntimeError("Chat model not loaded. Call load_chat_model() first.")
            
        return self.chat_model.generate_response(user_input, **kwargs)
        
    def prepare_chat_for_finetuning(self, **kwargs):
        """Prepare chat model for fine-tuning"""
        if not self._models_loaded["chat"] or self.chat_model is None:
            raise RuntimeError("Chat model not loaded. Call load_chat_model() first.")
            
        return self.chat_model.prepare_for_finetuning(**kwargs)
        
    def clear_chat_history(self):
        """Clear chat history"""
        if self.chat_model:
            self.chat_model.clear_history()
            
    def set_chat_system_prompt(self, prompt: str):
        """Set system prompt for chat model"""
        if self.chat_model:
            self.chat_model.set_system_prompt(prompt)
            
    def get_models_status(self) -> Dict[str, Any]:
        """Get status of all loaded models"""
        status = {
            "models_loaded": self._models_loaded,
            "memory_usage": {}
        }
        
        if self.chat_model:
            status["memory_usage"]["chat"] = self.chat_model.get_memory_usage()
            
        return status
        
    def unload_models(self):
        """Unload all models to free memory"""
        if self.chat_model:
            del self.chat_model
            self.chat_model = None
            self._models_loaded["chat"] = False
            
        if self.tts_model:
            del self.tts_model
            self.tts_model = None
            self._models_loaded["tts"] = False
            
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        logger.info("All models unloaded")

# Global instance
ai_models_manager = AIModelsManager()