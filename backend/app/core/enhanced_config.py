# backend/app/core/enhanced_config.py

"""
Enhanced Configuration cho hệ thống RAG với Qwen2.5-Instruct
Tập trung cấu hình cho RTX 3060 6GB và roleplay tối ưu
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import os
from pathlib import Path


@dataclass
class EnhancedModelConfig:
    """Cấu hình tối ưu cho Qwen2.5-Instruct trên RTX 3060 6GB"""
    
    # Model basics
    model_name: str = "gaianet/Qwen2.5-7B-Instruct-GGUF"
    model_file: str = "Qwen2.5-7B-Instruct-Q4_K_M.gguf"
    
    # Memory optimization for RTX 3060 6GB
    context_length: int = 4096  # Tăng context cho conversation dài
    max_tokens: int = 512       # Đủ cho phản hồi chi tiết
    n_gpu_layers: int = 28      # Tối ưu cho 6GB VRAM
    
    # Generation parameters for roleplay
    temperature: float = 0.8    # Tăng creativity cho roleplay
    top_p: float = 0.9         # Cân bằng creativity và consistency
    top_k: int = 40
    repeat_penalty: float = 1.15  # Tránh lặp lại
    
    # Performance
    n_threads: int = 8         # Cho 12700H
    use_mmap: bool = True
    use_mlock: bool = False
    verbose: bool = False


@dataclass
class CharacterRoleplayConfig:
    """Cấu hình cho roleplay nhân vật"""
    
    # Response requirements
    min_response_length: int = 150    # Tối thiểu 150 từ
    max_response_length: int = 600    # Tối đa 600 từ
    required_address: str = "chủ công"  # Xưng hô bắt buộc
    
    # Validation settings
    strict_character_validation: bool = True
    enhance_responses: bool = True
    
    # Conversation settings
    max_history_turns: int = 3        # Số turn lưu trong context
    reset_after_turns: int = 10       # Reset sau 10 turn để tránh context overflow


@dataclass
class PromptTemplateConfig:
    """Cấu hình template prompt"""
    
    # System prompt components
    include_identity: bool = True
    include_personality: bool = True
    include_thinking_style: bool = True
    include_speech_patterns: bool = True
    include_wisdom_sources: bool = True
    
    # User prompt components
    include_conversation_history: bool = True
    include_rag_context: bool = True
    max_rag_contexts: int = 3
    
    # Response structure
    require_greeting: bool = True
    require_conclusion: bool = True
    require_follow_up: bool = True


@dataclass
class RAGConfig:
    """Cấu hình cho RAG system"""
    
    # Embedding model
    embedding_model: str = "keepitreal/vietnamese-sbert"
    
    # Search parameters
    default_top_k: int = 3
    similarity_threshold: float = 0.7
    
    # Context processing
    max_context_length: int = 300     # Tối đa 300 ký tự per context
    context_overlap: int = 50         # Overlap giữa các chunk


class EnhancedSystemConfig:
    """Configuration manager cho enhanced system"""
    
    def __init__(self):
        self.model_config = EnhancedModelConfig()
        self.roleplay_config = CharacterRoleplayConfig()
        self.prompt_config = PromptTemplateConfig()
        self.rag_config = RAGConfig()
        
        # Load from environment if available
        self._load_from_env()
    
    def _load_from_env(self):
        """Load cấu hình từ environment variables"""
        
        # Model config from env
        if os.getenv("QWEN_CONTEXT_LENGTH"):
            self.model_config.context_length = int(os.getenv("QWEN_CONTEXT_LENGTH"))
        
        if os.getenv("QWEN_MAX_TOKENS"):
            self.model_config.max_tokens = int(os.getenv("QWEN_MAX_TOKENS"))
        
        if os.getenv("QWEN_GPU_LAYERS"):
            self.model_config.n_gpu_layers = int(os.getenv("QWEN_GPU_LAYERS"))
        
        if os.getenv("QWEN_TEMPERATURE"):
            self.model_config.temperature = float(os.getenv("QWEN_TEMPERATURE"))
        
        # Roleplay config from env
        if os.getenv("CHARACTER_ADDRESS_STYLE"):
            self.roleplay_config.required_address = os.getenv("CHARACTER_ADDRESS_STYLE")
        
        if os.getenv("MAX_HISTORY_TURNS"):
            self.roleplay_config.max_history_turns = int(os.getenv("MAX_HISTORY_TURNS"))
    
    def get_model_config_dict(self) -> Dict:
        """Get model config as dictionary for ChatAI"""
        return {
            "model_name": self.model_config.model_name,
            "model_file": self.model_config.model_file,
            "context_length": self.model_config.context_length,
            "max_tokens": self.model_config.max_tokens,
            "temperature": self.model_config.temperature,
            "top_p": self.model_config.top_p,
            "top_k": self.model_config.top_k,
            "repeat_penalty": self.model_config.repeat_penalty,
            "n_gpu_layers": self.model_config.n_gpu_layers,
            "n_threads": self.model_config.n_threads,
            "use_mmap": self.model_config.use_mmap,
            "use_mlock": self.model_config.use_mlock,
            "verbose": self.model_config.verbose
        }
    
    def validate_gpu_config(self) -> tuple[bool, str]:
        """Validate GPU configuration cho RTX 3060"""
        try:
            import torch
            
            if not torch.cuda.is_available():
                return False, "CUDA không khả dụng"
            
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
            
            if gpu_memory < 5.5:  # RTX 3060 có ~6GB
                return False, f"GPU memory ({gpu_memory:.1f}GB) có thể không đủ cho cấu hình hiện tại"
            
            # Check GPU layers vs memory
            estimated_memory = self.model_config.n_gpu_layers * 0.2  # Rough estimate
            if estimated_memory > gpu_memory * 0.8:  # Use max 80% of VRAM
                suggested_layers = int(gpu_memory * 0.8 / 0.2)
                return False, f"Số GPU layers ({self.model_config.n_gpu_layers}) quá cao. Đề xuất: {suggested_layers}"
            
            return True, "GPU configuration OK"
            
        except ImportError:
            return False, "PyTorch không được cài đặt"
        except Exception as e:
            return False, f"Lỗi kiểm tra GPU: {e}"
    
    def optimize_for_rtx3060(self):
        """Tối ưu cấu hình cho RTX 3060 6GB"""
        
        # Conservative settings for stable performance
        self.model_config.n_gpu_layers = 25      # An toàn cho 6GB
        self.model_config.context_length = 3072  # Reduce nếu cần
        self.model_config.max_tokens = 400       # Đủ cho most cases
        
        # Optimize for roleplay
        self.model_config.temperature = 0.8
        self.model_config.top_p = 0.9
        self.model_config.repeat_penalty = 1.15
        
        print("✅ Optimized configuration for RTX 3060 6GB")
    
    def print_current_config(self):
        """In ra cấu hình hiện tại"""
        print("📋 Current Enhanced System Configuration")
        print("=" * 50)
        
        print("🤖 Model Configuration:")
        print(f"  Model: {self.model_config.model_name}")
        print(f"  Context Length: {self.model_config.context_length}")
        print(f"  Max Tokens: {self.model_config.max_tokens}")
        print(f"  GPU Layers: {self.model_config.n_gpu_layers}")
        print(f"  Temperature: {self.model_config.temperature}")
        print(f"  Top-p: {self.model_config.top_p}")
        print(f"  Repeat Penalty: {self.model_config.repeat_penalty}")
        
        print("\n🎭 Roleplay Configuration:")
        print(f"  Required Address: {self.roleplay_config.required_address}")
        print(f"  Min Response Length: {self.roleplay_config.min_response_length}")
        print(f"  Max Response Length: {self.roleplay_config.max_response_length}")
        print(f"  Max History Turns: {self.roleplay_config.max_history_turns}")
        print(f"  Strict Validation: {self.roleplay_config.strict_character_validation}")
        
        print("\n🔍 RAG Configuration:")
        print(f"  Embedding Model: {self.rag_config.embedding_model}")
        print(f"  Default Top-K: {self.rag_config.default_top_k}")
        print(f"  Similarity Threshold: {self.rag_config.similarity_threshold}")


# Global singleton
_enhanced_config: Optional[EnhancedSystemConfig] = None

def get_enhanced_config() -> EnhancedSystemConfig:
    """Get singleton enhanced configuration"""
    global _enhanced_config
    if _enhanced_config is None:
        _enhanced_config = EnhancedSystemConfig()
    return _enhanced_config

def create_optimized_model_config() -> Dict:
    """Create optimized model config for immediate use"""
    config = get_enhanced_config()
    
    # Auto-optimize for RTX 3060
    is_valid, message = config.validate_gpu_config()
    if not is_valid:
        print(f"⚠️  GPU validation warning: {message}")
        config.optimize_for_rtx3060()
    
    return config.get_model_config_dict()
