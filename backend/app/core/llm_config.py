"""
LLM Configuration for PersonaRAG
Optimized for RTX 3060 6GB VRAM
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class QwenModelConfig:
    """Configuration for Qwen2.5-7B-Instruct model"""
    
    # Model settings
    model_name: str = "unsloth/Qwen2.5-7B-Instruct-unsloth-bnb-4bit"
    max_seq_length: int = 2048  # Reduced for 6GB VRAM
    load_in_4bit: bool = True   # Essential for 6GB VRAM
    device_map: str = "auto"
    
    # Generation settings
    max_new_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    repetition_penalty: float = 1.1
    do_sample: bool = True
    
    # Memory optimization
    use_gradient_checkpointing: bool = True
    dataloader_pin_memory: bool = False  # Disable for limited VRAM
    
    # System prompts
    default_system_prompt: str = """Bạn là một trợ lý AI thông minh và hữu ích. Hãy trả lời câu hỏi một cách chính xác, chi tiết và phù hợp với văn hóa Việt Nam. Luôn lịch sự và tôn trọng trong giao tiếp."""
    
    persona_system_prompts: Dict[str, str] = None
    
    def __post_init__(self):
        if self.persona_system_prompts is None:
            self.persona_system_prompts = {
                "friendly": "Bạn là một người bạn thân thiện và vui vẻ. Hãy trả lời với giọng điệu thân mật và ấm áp.",
                "professional": "Bạn là một chuyên gia tư vấn chuyên nghiệp. Hãy trả lời một cách chính xác và có căn cứ.",
                "creative": "Bạn là một nghệ sĩ sáng tạo. Hãy trả lời với óc tưởng tượng phong phú và độc đáo.",
                "teacher": "Bạn là một giáo viên kiên nhẫn. Hãy giải thích mọi thứ một cách dễ hiểu và chi tiết."
            }

@dataclass 
class LoRAConfig:
    """Configuration for LoRA fine-tuning"""
    
    # LoRA parameters optimized for 6GB VRAM
    r: int = 16  # Reduced rank
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    bias: str = "none"
    task_type: str = "CAUSAL_LM"
    
    # Target modules for Qwen2.5
    target_modules: List[str] = None
    
    # Training parameters
    learning_rate: float = 2e-4
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 1  # Small batch for 6GB VRAM
    gradient_accumulation_steps: int = 8  # Compensate for small batch
    warmup_ratio: float = 0.1
    weight_decay: float = 0.01
    
    # Memory optimization
    fp16: bool = True
    bf16: bool = False  # Use fp16 for RTX 3060
    dataloader_num_workers: int = 0  # Reduce CPU usage
    remove_unused_columns: bool = True
    
    # Saving
    save_steps: int = 250
    save_total_limit: int = 3
    logging_steps: int = 50
    
    def __post_init__(self):
        if self.target_modules is None:
            # Qwen2.5 specific modules
            self.target_modules = [
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj"
            ]

@dataclass
class HardwareConfig:
    """Hardware-specific configuration"""
    
    # GPU settings for RTX 3060
    gpu_memory_limit: float = 5.5  # GB, leave some headroom
    max_memory_usage_threshold: float = 0.9
    enable_memory_efficient_attention: bool = True
    
    # CPU settings
    num_cpu_cores: int = 12  # i7-12700H has 12 threads
    max_cpu_usage: float = 0.8
    
    # System RAM
    system_ram_gb: int = 32
    
    @classmethod
    def get_optimal_batch_size(cls, seq_length: int, model_size_gb: float) -> int:
        """Calculate optimal batch size based on available VRAM"""
        available_vram = cls.gpu_memory_limit - model_size_gb
        
        # Rough estimation: 1024 tokens ≈ 0.1GB with gradients
        tokens_per_gb = 10240  # Conservative estimate
        max_tokens = int(available_vram * tokens_per_gb)
        
        batch_size = max(1, max_tokens // seq_length)
        return min(batch_size, 4)  # Cap at 4 for stability

# Global configurations
QWEN_CONFIG = QwenModelConfig()
LORA_CONFIG = LoRAConfig()
HARDWARE_CONFIG = HardwareConfig()

# Model variants for different use cases
MODEL_VARIANTS = {
    "base": {
        "model_name": "unsloth/Qwen2.5-7B-Instruct-unsloth-bnb-4bit",
        "description": "Base Qwen2.5-7B with 4-bit quantization",
        "vram_usage_gb": 4.5,
        "recommended_seq_length": 2048
    },
    "extended": {
        "model_name": "unsloth/Qwen2.5-7B-Instruct-unsloth-bnb-4bit",
        "description": "Extended context version",
        "vram_usage_gb": 5.0,
        "recommended_seq_length": 4096,
        "note": "May require careful memory management"
    }
}

def get_config_for_hardware() -> Dict[str, Any]:
    """Get optimized configuration for current hardware"""
    return {
        "model_config": QWEN_CONFIG,
        "lora_config": LORA_CONFIG,
        "hardware_config": HARDWARE_CONFIG,
        "recommended_variant": "base",  # Safe choice for RTX 3060
        "optimization_notes": [
            "Using 4-bit quantization for memory efficiency",
            "Reduced batch size to fit 6GB VRAM",
            "Gradient accumulation to maintain effective batch size",
            "FP16 precision for RTX 3060 compatibility"
        ]
    }
