# Chat AI với GGUF Models

Hệ thống Chat AI sử dụng mô hình GGUF Qwen2.5-7B-Instruct, được tối ưu hóa cho RTX 3060 6GB.

## Tính năng

- 🤖 Chat AI thông minh với mô hình Qwen2.5-7B
- 🚀 Hỗ trợ GPU acceleration (CUDA)
- 💾 Quản lý bộ nhớ thông minh cho RTX 3060 6GB
- 📡 Streaming response
- 🗣️ Hỗ trợ tiếng Việt
- 🔄 API RESTful hoàn chỉnh

## Cấu hình hệ thống

### Yêu cầu

- **CPU**: Intel 12700H (8 threads được sử dụng)
- **GPU**: RTX 3060 6GB VRAM
- **RAM**: 32GB (khuyến nghị tối thiểu 16GB)
- **Storage**: ~10GB để lưu models

### Cấu hình mô hình được tối ưu

```python
ModelConfig(
    model_name="gaianet/Qwen2.5-7B-Instruct-GGUF",
    model_file="qwen2.5-7b-instruct-q4_k_m.gguf",  # 4.68GB
    context_length=4096,      # Phù hợp với 6GB VRAM
    max_tokens=512,
    n_gpu_layers=25,          # Số lớp chạy trên GPU
    n_threads=8,              # Cho 12700H
    temperature=0.7
)
```

## Cài đặt

### 1. Cài đặt dependencies

#### Sử dụng Poetry (khuyến nghị):

```bash
# Chạy script tự động
cd backend
install_chat_dependencies.bat

# Hoặc cài đặt thủ công:
poetry install
poetry add llama-cpp-python --extras="cuda"
poetry add huggingface_hub pydantic-settings
```

#### Sử dụng pip:

```bash
pip install -r requirements.txt
pip install llama-cpp-python huggingface_hub pydantic-settings
```

### 2. Kiểm tra cài đặt

```bash
# Test đơn giản
poetry run python simple_chat_test.py

# Test đầy đủ
poetry run python test_chat_ai.py
```

## Sử dụng

### 1. Test Chat AI độc lập

```python
from app.core.ai_models import ChatAI, ModelConfig

# Tạo cấu hình
config = ModelConfig(
    model_file="qwen2.5-7b-instruct-q4_k_m.gguf",
    n_gpu_layers=25,
    temperature=0.7
)

# Khởi tạo chat AI
chat_ai = ChatAI(config)
chat_ai.load_model()

# Chat
response = chat_ai.chat("Xin chào! Bạn có thể giúp tôi không?")
print(response)
```

### 2. Sử dụng API

#### Khởi động server:

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### API Endpoints:

**Chat thường:**

```bash
curl -X POST "http://localhost:8000/api/v1/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Xin chào!",
    "system_prompt": "Bạn là trợ lý AI thông minh",
    "reset_history": false
  }'
```

**Stream chat:**

```bash
curl -X POST "http://localhost:8000/api/v1/ai/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Kể cho tôi một câu chuyện ngắn"
  }'
```

**Quản lý model:**

```bash
# Load model
curl -X POST "http://localhost:8000/api/v1/ai/model/load"

# Thông tin model
curl -X GET "http://localhost:8000/api/v1/ai/model/info"

# Unload model
curl -X POST "http://localhost:8000/api/v1/ai/model/unload"
```

## Tối ưu hóa cho RTX 3060 6GB

### Cấu hình VRAM thấp:

```python
ModelConfig(
    model_file="qwen2.5-7b-instruct-q4_0.gguf",  # 4.43GB
    context_length=2048,     # Giảm context
    n_gpu_layers=20,         # Ít layer hơn trên GPU
    max_tokens=256
)
```

### Cấu hình VRAM cao:

```python
ModelConfig(
    model_file="qwen2.5-7b-instruct-q5_k_m.gguf",  # 5.44GB
    context_length=4096,
    n_gpu_layers=30,
    max_tokens=512
)
```

## Các file quan trọng

### Core Components:

- `app/core/ai_models.py`: Lớp ChatAI chính
- `app/api/v1/chat_ai.py`: API endpoints
- `test_chat_ai.py`: Test suite đầy đủ
- `simple_chat_test.py`: Test nhanh

### Configuration:

- `pyproject.toml`: Dependencies
- `install_chat_dependencies.bat`: Script cài đặt

## Troubleshooting

### Lỗi CUDA:

```bash
# Kiểm tra CUDA
poetry run python -c "import torch; print(torch.cuda.is_available())"

# Cài lại llama-cpp-python với CUDA
set CMAKE_ARGS=-DLLAMA_CUBLAS=on
poetry run pip install llama-cpp-python --force-reinstall --no-cache-dir
```

### Thiếu VRAM:

- Giảm `n_gpu_layers`
- Giảm `context_length`
- Sử dụng model nhỏ hơn (Q4_0 thay vì Q4_K_M)

### Model download chậm:

```bash
# Download trước bằng huggingface-cli
huggingface-cli download gaianet/Qwen2.5-7B-Instruct-GGUF qwen2.5-7b-instruct-q4_k_m.gguf
```

## Performance Benchmarks

Trên RTX 3060 6GB + 12700H:

- **Load time**: ~30-60 giây
- **Response speed**: ~15-25 tokens/giây
- **VRAM usage**: ~5.5GB (Q4_K_M)
- **Context length**: 4096 tokens

## API Documentation

Truy cập http://localhost:8000/docs để xem Swagger UI với tài liệu API đầy đủ.

## Tích hợp

Để tích hợp vào ứng dụng chính:

1. Chat AI đã được thêm vào `main.py`
2. API endpoints có prefix `/api/v1/ai/`
3. Có thể sử dụng cùng với TTS và RAG
4. Hỗ trợ streaming cho real-time chat

## Phát triển tiếp

- [ ] Fine-tuning cho domain cụ thể
- [ ] Tích hợp với RAG system
- [ ] Multi-model support
- [ ] Voice integration
- [ ] Chat history persistence
