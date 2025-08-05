# PersonaRAG - Hệ thống RAG cho Nhân vật Lịch sử

## Tổng quan

PersonaRAG là một hệ thống RAG (Retrieval-Augmented Generation) tiên tiến, cho phép các nhân vật lịch sử như **Gia Cát Lượng** và **Tư Mã Ý** tư vấn cho sinh viên dựa trên kiến thức và kinh nghiệm lịch sử của họ.

### Kiến trúc hệ thống

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API    │    │  Vector Store   │
│   (React)       │◄──►│   (FastAPI)      │◄──►│   (ChromaDB)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   LLM Engine     │
                       │ (Qwen2.5-7B)     │
                       └──────────────────┘
```

## Tính năng chính

### 🎭 Nhân vật Lịch sử

- **Gia Cát Lượng**: Quân sư tài ba, chuyên về chiến lược và leadership
- **Tư Mã Ý**: Nhà chiến lược thâm trầm, chuyên về kiên nhẫn và kế hoạch dài hạn
- Có thể mở rộng thêm nhân vật khác

### 🧠 RAG Engine

- **Vector Database**: ChromaDB cho tìm kiếm semantic
- **Embeddings**: Vietnamese-SBERT cho text tiếng Việt
- **Context Retrieval**: Tìm kiếm thông tin liên quan theo character
- **Smart Prompting**: Xây dựng prompt động theo tính cách nhân vật

### 💬 Tương tác Thông minh

- Chat với nhân vật theo tính cách riêng biệt
- Lời khuyên dựa trên tích sử và kinh nghiệm lịch sử
- Hỗ trợ conversation history và context

## Cài đặt

### 1. Requirements

```bash
# Core dependencies
pip install -r requirements.txt

# RAG dependencies
pip install -r requirements_rag.txt
```

### 2. Setup Vector Database

```bash
# Chạy script setup RAG system
python scripts/setup_rag_system.py
```

### 3. Test hệ thống

```bash
# Test cơ bản (không cần dependencies đầy đủ)
python scripts/test_rag_simple.py

# Test đầy đủ với vector database
python scripts/test_rag_system.py
```

## Sử dụng

### 1. Start Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. API Endpoints

#### Danh sách nhân vật

```bash
GET /api/v1/rag/characters
```

#### Khởi tạo Knowledge Base

```bash
POST /api/v1/rag/knowledge-base/initialize
{
    "character_ids": ["zhuge_liang", "sima_yi"],
    "force_recreate": false
}
```

#### Tìm kiếm context

```bash
POST /api/v1/rag/search
{
    "query": "leadership skills",
    "character_id": "zhuge_liang",
    "top_k": 5
}
```

#### Xin lời khuyên

```bash
POST /api/v1/rag/advice
{
    "user_question": "Làm thế nào để trở thành leader giỏi?",
    "character_id": "zhuge_liang",
    "context": "Tôi là sinh viên năm cuối"
}
```

### 3. Web UI

Truy cập: `http://localhost:8000/docs` để xem Swagger UI

## Cấu trúc dữ liệu

### Character Profile

```json
{
  "id": "zhuge_liang",
  "name": "Gia Cát Lượng",
  "dynasty": "Tam Quốc",
  "personality_traits": ["Thông minh", "Trung thành"],
  "expertise": ["Quân sự", "Chính trị"],
  "advice_style": "Sâu sắc, thực tế",
  "speaking_style": "Lịch thiệp, khiêm tốn"
}
```

### Character Stories

```json
{
  "id": "gc_001",
  "title": "Tam cố thảo lư",
  "category": "leadership",
  "content": "...",
  "lesson": "Sự chân thành và kiên nhẫn...",
  "tags": ["leadership", "persistence"],
  "relevance_score": 0.9
}
```

## Cấu hình

### Vector Database

- **Engine**: ChromaDB
- **Embedding Model**: keepitreal/vietnamese-sbert
- **Chunk Size**: 512 tokens
- **Top-K Results**: 5

### LLM Settings

- **Model**: Qwen2.5-7B-Instruct-GGUF
- **Context Length**: 4096 tokens
- **Temperature**: 0.7

## Phát triển

### Thêm nhân vật mới

1. **Tạo character profile** trong `app/models/characters.py`
2. **Thêm dữ liệu training** trong `data/training/{character_id}/`
3. **Cập nhật prompt templates** trong `app/core/prompt_builder.py`

### Thêm dữ liệu stories

1. **Tạo file JSON** với format chuẩn
2. **Run script** để load vào vector database
3. **Test** với các query mẫu

### Customization

- **Embedding Model**: Thay đổi trong `RAGAgent.__init__()`
- **Chunk Strategy**: Tùy chỉnh trong `RAGAgent._chunk_text()`
- **Prompt Templates**: Chỉnh sửa trong `CharacterPromptBuilder`

## API Reference

### RAG Endpoints

| Endpoint                         | Method | Description             |
| -------------------------------- | ------ | ----------------------- |
| `/rag/characters`                | GET    | Danh sách nhân vật      |
| `/rag/characters/{id}`           | GET    | Thông tin nhân vật      |
| `/rag/knowledge-base/initialize` | POST   | Khởi tạo knowledge base |
| `/rag/knowledge-base/stats`      | GET    | Thống kê knowledge base |
| `/rag/search`                    | POST   | Tìm kiếm context        |
| `/rag/advice`                    | POST   | Xin lời khuyên          |
| `/rag/health`                    | GET    | Health check            |

### Response Format

```json
{
  "character_id": "zhuge_liang",
  "character_name": "Gia Cát Lượng",
  "advice": "Dựa trên kinh nghiệm của ta...",
  "relevant_stories": ["gc_001", "gc_002"],
  "confidence_score": 0.85,
  "response_time": 1.23
}
```

## Troubleshooting

### Lỗi import dependencies

```bash
pip install sentence-transformers chromadb
```

### Lỗi vector database

```bash
# Xóa và tạo lại
rm -rf data/chroma_db
python scripts/setup_rag_system.py
```

### Lỗi encoding trên Windows

- Hệ thống đã tự động xử lý encoding UTF-8
- Nếu vẫn lỗi, check Python version >= 3.8

## Performance

### Benchmarks (RTX 3060 6GB)

- **Embedding Generation**: ~0.1s/document
- **Vector Search**: ~0.05s/query
- **Full RAG Response**: ~2-3s/query
- **Memory Usage**: ~2GB (vector store + embeddings)

### Optimization Tips

- **Batch Processing**: Load nhiều documents cùng lúc
- **Caching**: Cache embeddings cho queries phổ biến
- **Chunk Optimization**: Điều chỉnh chunk size phù hợp

## Roadmap

### Phase 1 ✅

- [x] Basic RAG architecture
- [x] Character models và stories
- [x] Vector database integration
- [x] API endpoints

### Phase 2 🔄

- [ ] Advanced prompt engineering
- [ ] Multi-turn conversation
- [ ] Character voice integration
- [ ] Performance optimization

### Phase 3 📋

- [ ] Multi-language support
- [ ] More historical characters
- [ ] Advanced analytics
- [ ] Mobile app integration

## Contributing

1. Fork repository
2. Create feature branch
3. Thêm tests cho features mới
4. Submit pull request

## License

MIT License - xem file LICENSE để biết chi tiết.

---

Made with ❤️ for preserving historical wisdom through AI
