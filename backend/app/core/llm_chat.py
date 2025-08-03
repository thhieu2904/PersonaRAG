"""
LLM Chat module with Qwen2.5-7B-Instruct using Unsloth for fine-tuning capability
"""

import torch
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Represents a chat message"""
    role: str  # "user", "assistant", "system"
    content: str

class QwenChatModel:
    """
    Qwen2.5-7B-Instruct chat model with Unsloth integration for fine-tuning
    Optimized for RTX 3060 6GB VRAM configuration
    """
    
    def __init__(
        self,
        model_name: str = "unsloth/Qwen2.5-7B-Instruct-unsloth-bnb-4bit",
        max_seq_length: int = 2048,
        dtype: Optional[torch.dtype] = None,
        load_in_4bit: bool = True,
        device_map: str = "auto"
    ):
        """
        Initialize Qwen chat model with Unsloth optimizations
        
        Args:
            model_name: HuggingFace model name
            max_seq_length: Maximum sequence length
            dtype: Data type for model weights
            load_in_4bit: Use 4-bit quantization for VRAM efficiency
            device_map: Device mapping strategy
        """
        self.model_name = model_name
        self.max_seq_length = max_seq_length
        self.load_in_4bit = load_in_4bit
        self.device_map = device_map
        
        self.model = None
        self.tokenizer = None
        self.chat_history: List[ChatMessage] = []
        
        # System prompt for Vietnamese persona
        self.system_prompt = """Bạn là một trợ lý AI thông minh và hữu ích. Hãy trả lời câu hỏi một cách chính xác, chi tiết và phù hợp với văn hóa Việt Nam. Luôn lịch sự và tôn trọng trong giao tiếp."""
        
    def load_model(self):
        """Load the Qwen model using Unsloth for optimization"""
        # Skip Unsloth on Windows due to triton issues, use fallback directly
        import platform
        if platform.system() == "Windows":
            logger.info("Windows detected, using transformers fallback (Unsloth has triton issues on Windows)")
            self._load_fallback_model()
            return
            
        try:
            from unsloth import FastLanguageModel
            
            logger.info(f"Loading {self.model_name} with Unsloth optimizations...")
            
            # Load model and tokenizer with Unsloth optimizations
            self.model, self.tokenizer = FastLanguageModel.from_pretrained(
                model_name=self.model_name,
                max_seq_length=self.max_seq_length,
                dtype=self.dtype,
                load_in_4bit=self.load_in_4bit,
                device_map=self.device_map,
            )
            
            # Set pad token if not exists
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            logger.info("Model loaded successfully with Unsloth!")
            
        except ImportError as e:
            logger.error(f"Unsloth import error: {e}. Using fallback...")
            self._load_fallback_model()
        except Exception as e:
            logger.error(f"Error loading model with Unsloth: {e}")
            logger.info("Trying fallback loading method...")
            self._load_fallback_model()
            
    def _load_fallback_model(self):
        """Fallback to standard transformers if Unsloth is not available"""
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        
        logger.info("Loading model with standard transformers...")
        
        # Use base Qwen model if unsloth version fails
        base_model_name = self.model_name.replace("-unsloth-bnb-4bit", "")
        if base_model_name.startswith("unsloth/"):
            base_model_name = base_model_name.replace("unsloth/", "Qwen/")
            
        logger.info(f"Loading base model: {base_model_name}")
        
        # Skip quantization for CPU offloading compatibility
        # Use FP16 + CPU offloading instead (tested working on RTX 3060 6GB)
        bnb_config = None
        logger.info("Using FP16 + CPU offloading (no quantization) for 6GB VRAM compatibility")
        
        # Optimized device map for 6GB VRAM - based on successful test
        device_map = {
            "model.embed_tokens": "cuda:0",
            "model.norm": "cpu",        # Move norm to CPU to save VRAM
            "lm_head": "cpu",           # Move head to CPU to save VRAM
        }
        
        # Conservative approach: Only first 16 layers on GPU
        # This configuration successfully tested on RTX 3060 6GB
        num_layers = 32  # Qwen2.5-7B has 32 layers
        gpu_layers = 16   # Conservative: only 16 layers on GPU
        
        for i in range(gpu_layers):  # Layers 0-15 on GPU
            device_map[f"model.layers.{i}"] = "cuda:0"
        for i in range(gpu_layers, num_layers):  # Layers 16-31 on CPU
            device_map[f"model.layers.{i}"] = "cpu"
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                base_model_name,
                trust_remote_code=True,
                use_fast=True
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                device_map=device_map,
                torch_dtype=torch.float16,  # Use FP16 for memory efficiency
                trust_remote_code=True,
                low_cpu_mem_usage=True,
                # Conservative memory limits based on successful test
                max_memory={0: "4GB", "cpu": "25GB"},
                offload_folder="./temp_offload"
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            logger.info("Model loaded successfully with fallback method!")
            
        except Exception as e:
            logger.error(f"Failed to load with FP16 settings: {e}")
            raise RuntimeError(f"Cannot load Qwen2.5-7B on this hardware: {e}")
            # No more fallback attempts - if FP16 fails, hardware is insufficient
            
    def prepare_for_finetuning(self, 
                              target_modules: List[str] = None,
                              r: int = 16,
                              lora_alpha: int = 32,
                              lora_dropout: float = 0.05,
                              bias: str = "none",
                              task_type: str = "CAUSAL_LM"):
        """
        Prepare model for LoRA fine-tuning using Unsloth
        
        Args:
            target_modules: Target modules for LoRA adaptation
            r: LoRA rank
            lora_alpha: LoRA alpha parameter
            lora_dropout: LoRA dropout rate
            bias: Bias configuration
            task_type: Task type for PEFT
        """
        try:
            from unsloth import FastLanguageModel
            from peft import LoraConfig, TaskType
            
            if target_modules is None:
                target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                                "gate_proj", "up_proj", "down_proj"]
            
            # Add LoRA adapters using Unsloth
            self.model = FastLanguageModel.get_peft_model(
                self.model,
                r=r,
                target_modules=target_modules,
                lora_alpha=lora_alpha,
                lora_dropout=lora_dropout,
                bias=bias,
                use_gradient_checkpointing="unsloth",
                random_state=3407,
                use_rslora=False,
                loftq_config=None,
            )
            
            logger.info("Model prepared for fine-tuning with LoRA adapters")
            
        except ImportError:
            logger.error("Unsloth not available for fine-tuning preparation")
            raise
        except Exception as e:
            logger.error(f"Error preparing model for fine-tuning: {e}")
            raise
            
    def format_chat_prompt(self, messages: List[ChatMessage]) -> str:
        """Format chat messages into Qwen prompt format"""
        formatted_messages = []
        
        # Add system message if provided
        if self.system_prompt:
            formatted_messages.append(f"<|im_start|>system\n{self.system_prompt}<|im_end|>")
        
        # Add conversation messages
        for message in messages:
            formatted_messages.append(f"<|im_start|>{message.role}\n{message.content}<|im_end|>")
        
        # Add assistant start token for generation
        formatted_messages.append("<|im_start|>assistant")
        
        return "\n".join(formatted_messages)
        
    def generate_response(self, 
                         user_input: str, 
                         max_new_tokens: int = 512,
                         temperature: float = 0.7,
                         top_p: float = 0.9,
                         do_sample: bool = True,
                         pad_token_id: Optional[int] = None) -> str:
        """
        Generate response for user input
        
        Args:
            user_input: User's message
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            do_sample: Whether to use sampling
            pad_token_id: Padding token ID
            
        Returns:
            Generated response text
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
            
        # Add user message to history
        user_message = ChatMessage(role="user", content=user_input)
        current_messages = self.chat_history + [user_message]
        
        # Format prompt
        prompt = self.format_chat_prompt(current_messages)
        
        # Tokenize
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_seq_length - max_new_tokens
        )
        
        # For mixed device models, ensure tensors are on the correct device
        if torch.cuda.is_available():
            # Don't move inputs to specific device - let the model handle device placement
            # This works better with CPU offloaded models
            pass
            
        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=do_sample,
                pad_token_id=pad_token_id or self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                use_cache=True
            )
        
        # Decode response
        response = self.tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:], 
            skip_special_tokens=True
        ).strip()
        
        # Add messages to history
        assistant_message = ChatMessage(role="assistant", content=response)
        self.chat_history.append(user_message)
        self.chat_history.append(assistant_message)
        
        # Keep only last 10 exchanges to manage memory
        if len(self.chat_history) > 20:
            self.chat_history = self.chat_history[-20:]
            
        return response
        
    def clear_history(self):
        """Clear chat history"""
        self.chat_history.clear()
        
    def set_system_prompt(self, prompt: str):
        """Set system prompt"""
        self.system_prompt = prompt
        
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current GPU memory usage"""
        if torch.cuda.is_available():
            return {
                "allocated": torch.cuda.memory_allocated() / 1024**3,  # GB
                "reserved": torch.cuda.memory_reserved() / 1024**3,    # GB
                "max_allocated": torch.cuda.max_memory_allocated() / 1024**3,  # GB
            }
        return {}
        
    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            if hasattr(self, 'model') and self.model is not None:
                del self.model
            if hasattr(self, 'tokenizer') and self.tokenizer is not None:
                del self.tokenizer
            if torch is not None and torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass  # Ignore cleanup errors
