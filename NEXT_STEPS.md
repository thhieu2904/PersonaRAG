# PersonaRAG - Next Steps Guide

## 🎉 Chúc mừng! Hệ thống RAG đã sẵn sàng!

Bạn đã thành công xây dựng một hệ thống RAG hoàn chỉnh với các nhân vật lịch sử Gia Cát Lượng và Tư Mã Ý. Dưới đây là các bước tiếp theo:

## 🚀 1. Khởi động Server

### Phương pháp 1: Sử dụng batch file (Dễ nhất)

```bash
# Từ folder backend
start_server.bat
```

### Phương pháp 2: Command line

```bash
cd backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Phương pháp 3: Python script

```bash
cd backend
poetry run python start_server.py
```

## 🌐 2. Truy cập API

Sau khi server khởi động, bạn có thể truy cập:

- **API Documentation**: http://localhost:8000/docs
- **API Alternative Docs**: http://localhost:8000/redoc
- **Main API**: http://localhost:8000/api/v1/

## 🧪 3. Test API

```bash
# Test API endpoints
poetry run python test_api.py

# Test chat demo
poetry run python scripts/demo_rag_chat.py

# Test full integration
poetry run python scripts/test_full_rag_integration.py
```

## 📱 4. Sử dụng API

### Lấy danh sách nhân vật:

```bash
GET http://localhost:8000/api/v1/characters/
```

### Chat với nhân vật:

```bash
POST http://localhost:8000/api/v1/chat/advice
{
    "character_id": "zhuge_liang",
    "message": "Tôi cần lời khuyên về lãnh đạo"
}
```

### Lấy thông tin nhân vật:

```bash
GET http://localhost:8000/api/v1/characters/zhuge_liang
```

## 🔧 5. Customization

### Thêm nhân vật mới:

1. Tạo folder trong `data/training/ten_nhan_vat/`
2. Thêm `personality.json` và `conversations.json`
3. Cập nhật `app/models/characters.py`
4. Chạy lại `scripts/setup_rag_system.py`

### Thêm câu chuyện mới:

1. Chỉnh sửa file `conversations.json` trong folder nhân vật
2. Chạy lại setup để cập nhật vector database

### Thay đổi AI model:

- Chỉnh sửa `app/core/ai_models.py`
- Cập nhật model path và config

## 🎯 6. Production Deployment

### Docker:

```bash
# Build and run with docker-compose
docker-compose up --build
```

### Manual deployment:

```bash
# Install production dependencies
poetry install --no-dev

# Run with gunicorn
poetry run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📊 7. Monitoring

### Check vector database:

```python
from app.core.rag_agent import RAGAgent
agent = RAGAgent()
stats = agent.get_collection_stats()
print(f"Documents: {stats['total_documents']}")
```

### Performance metrics:

- Vector similarity scores
- Response time
- Memory usage
- GPU utilization (if using CUDA)

## 🛠 8. Troubleshooting

### Common issues:

1. **Server won't start**:

   - Check if port 8000 is available
   - Verify all dependencies installed: `poetry install`

2. **RAG not working**:

   - Run setup again: `poetry run python scripts/setup_rag_system.py`
   - Check vector database: `ls data/chroma_db/`

3. **Unicode errors**:

   - Set environment: `set PYTHONIOENCODING=utf-8`
   - Use proper encoding in code

4. **Memory issues**:
   - Reduce batch size in embedding
   - Use lighter models
   - Increase system RAM

## 📈 9. Future Enhancements

- [ ] Add more historical characters
- [ ] Implement conversation memory
- [ ] Add voice synthesis (TTS)
- [ ] Create web frontend
- [ ] Add user authentication
- [ ] Implement conversation analytics
- [ ] Add multi-language support

## 🎓 10. Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **ChromaDB**: https://docs.trychroma.com/
- **RAG**: https://arxiv.org/abs/2005.11401
- **Vector Embeddings**: https://platform.openai.com/docs/guides/embeddings

---

## 🎉 Congratulations!

Bạn đã có một hệ thống RAG hoàn chỉnh với:

- ✅ Vector database (ChromaDB)
- ✅ Vietnamese embeddings
- ✅ Character personalities
- ✅ REST API
- ✅ Interactive chat
- ✅ Production ready

**Happy coding!** 🚀
