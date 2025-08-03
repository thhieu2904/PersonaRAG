# PersonaRAG LLM Integration

Tích hợp mô hình ngôn ngữ lớn Qwen2.5-7B-Instruct với khả năng fine-tuning LoRA cho PersonaRAG.

## 🎯 Tính năng chính

- **Qwen2.5-7B-Instruct**: Mô hình chat AI tiên tiến với 7 tỷ tham số
- **Unsloth Optimization**: Tối ưu hóa tốc độ và bộ nhớ
- **4-bit Quantization**: Giảm sử dụng VRAM xuống còn ~4.5GB
- **LoRA Fine-tuning**: Khả năng fine-tune với tài nguyên hạn chế
- **Vietnamese Support**: Hỗ trợ tiếng Việt tự nhiên

## 🖥️ Yêu cầu hệ thống

### Cấu hình tối thiểu (RTX 3060 6GB)

- **GPU**: RTX 3060 với 6GB VRAM
- **CPU**: i7-12700H hoặc tương đương
- **RAM**: 32GB hệ thống
- **Storage**: 20GB dung lượng trống

### Phần mềm

- Python 3.11
- CUDA 12.1+
- Poetry package manager

## 🚀 Cài đặt nhanh

### 1. Chạy script setup

```bash
cd backend/scripts
setup_llm.bat
```

### 2. Cài đặt thủ công

```bash
# Cài đặt dependencies cơ bản
poetry install

# Thêm dependencies cho LLM
poetry add peft bitsandbytes psutil
```

## 🧪 Kiểm tra và sử dụng

### 1. Test cơ bản

```bash
poetry run python test_qwen_chat.py
```

### 2. Chat tương tác

```bash
poetry run python test_qwen_chat.py --interactive
```

### 3. Test fine-tuning preparation

```bash
poetry run python test_qwen_chat.py --test-finetuning
```

## 📋 Sử dụng trong code

### Load model và chat cơ bản

```python
from app.core.ai_models import ai_models_manager

# Load model
ai_models_manager.load_chat_model()

# Chat
response = ai_models_manager.generate_chat_response(
    "Xin chào! Bạn có khỏe không?"
)
print(response)
```

### Chuẩn bị fine-tuning

```python
# Prepare for LoRA fine-tuning
ai_models_manager.prepare_chat_for_finetuning(
    r=16,  # LoRA rank
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]
)
```

### Cấu hình persona khác nhau

```python
# Set system prompt cho persona
ai_models_manager.set_chat_system_prompt(
    "Bạn là một giáo viên kiên nhẫn và nhiệt tình..."
)
```

## ⚙️ Cấu hình cho RTX 3060

### Memory Optimization

```python
# Cấu hình tối ưu cho 6GB VRAM
config = {
    "max_seq_length": 2048,      # Giảm độ dài sequence
    "load_in_4bit": True,        # Bắt buộc 4-bit quantization
    "batch_size": 1,             # Batch size nhỏ
    "gradient_accumulation": 8,   # Bù trừ batch size nhỏ
}
```

### LoRA Parameters

```python
# Cấu hình LoRA phù hợp với 6GB VRAM
lora_config = {
    "r": 16,                     # Rank thấp hơn
    "lora_alpha": 32,
    "lora_dropout": 0.05,
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"]
}
```

## 🔧 Troubleshooting

### Out of Memory (OOM) Errors

```bash
# Giảm sequence length
max_seq_length = 1024

# Giảm batch size
per_device_batch_size = 1

# Tăng gradient accumulation
gradient_accumulation_steps = 16
```

### Slow Generation

```bash
# Sử dụng caching
use_cache = True

# Giảm số tokens generate
max_new_tokens = 256

# Tắt sampling để nhanh hơn
do_sample = False
```

### Model Loading Issues

```bash
# Xóa cache nếu có lỗi
rm -rf ~/.cache/huggingface/

# Cài đặt lại unsloth
poetry remove unsloth
poetry add git+https://github.com/unslothai/unsloth.git
```

## 📊 Performance Benchmarks

### RTX 3060 6GB Performance

- **Loading time**: ~2-3 phút
- **Memory usage**: ~4.5GB VRAM
- **Generation speed**: ~15-20 tokens/giây
- **Fine-tuning speed**: ~0.5 steps/giây

### Memory Usage Breakdown

```
Model weights (4-bit): ~3.5GB
Activation memory: ~0.8GB
LoRA adapters: ~0.1GB
Buffer: ~0.1GB
Total: ~4.5GB / 6GB
```

## 🎨 Persona System Prompts

### Friendly Assistant

```python
prompt = "Bạn là một người bạn thân thiện và vui vẻ. Hãy trả lời với giọng điệu thân mật và ấm áp."
```

### Professional Advisor

```python
prompt = "Bạn là một chuyên gia tư vấn chuyên nghiệp. Hãy trả lời một cách chính xác và có căn cứ."
```

### Creative Writer

```python
prompt = "Bạn là một nghệ sĩ sáng tạo. Hãy trả lời với óc tưởng tượng phong phú và độc đáo."
```

## 🔄 Integration với F5-TTS

```python
# Workflow: Text -> LLM -> TTS -> Audio
user_input = "Kể cho tôi một câu chuyện ngắn"

# 1. Generate text response
text_response = ai_models_manager.generate_chat_response(user_input)

# 2. Convert to speech with F5-TTS (TODO)
# audio = tts_service.synthesize(text_response, voice_profile="gia_cat_luong")
```

## 📝 Logs và Monitoring

### Check GPU Memory

```python
status = ai_models_manager.get_models_status()
print(f"GPU Memory: {status['memory_usage']['chat']['allocated']:.2f} GB")
```

### Training Logs

```bash
# Sử dụng wandb cho monitoring (optional)
poetry add wandb
wandb login
```

## 🛠️ Development Notes

### Model Architecture

- **Base Model**: Qwen2.5-7B-Instruct
- **Quantization**: BitsAndBytesConfig 4-bit NF4
- **Optimization**: Unsloth + Flash Attention
- **Fine-tuning**: LoRA (Low-Rank Adaptation)

### File Structure

```
backend/
├── app/core/
│   ├── llm_chat.py         # Main chat model class
│   ├── llm_config.py       # Configuration settings
│   └── ai_models.py        # Models manager
├── test_qwen_chat.py       # Test script
└── scripts/
    └── setup_llm.bat       # Setup script
```

## 🔗 Tài liệu tham khảo

- [Unsloth Documentation](https://github.com/unslothai/unsloth)
- [Qwen2.5 Model Card](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)
- [PEFT Documentation](https://huggingface.co/docs/peft)
- [BitsAndBytesConfig](https://huggingface.co/docs/transformers/main_classes/quantization)

## 📞 Hỗ trợ

Nếu gặp vấn đề:

1. Kiểm tra system requirements
2. Chạy `test_qwen_chat.py` để debug
3. Kiểm tra GPU memory với `nvidia-smi`
4. Xem logs trong console output
