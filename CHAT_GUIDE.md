# 🎭 PersonaRAG - Chat với Nhân Vật Lịch Sử

## 🚀 Khởi động nhanh

### Phương pháp 1: Khởi động tự động (Khuyến nghị)

```bash
# Chạy file bat để khởi động cả backend + frontend
start_full_stack.bat
```

### Phương pháp 2: Khởi động thủ công

**Backend:**

```bash
cd backend
set PYTHONIOENCODING=utf-8
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
cd frontend
npm run dev
```

## 🌐 Truy cập ứng dụng

- **💬 Chat Interface**: http://localhost:5173
- **📚 API Documentation**: http://localhost:8000/docs
- **🔧 Backend API**: http://localhost:8000

## 🎯 Tính năng chính

### 1. Chat với nhân vật lịch sử

- **Gia Cát Lượng**: Chuyên gia chiến lược, lãnh đạo
- **Tư Mã Ý**: Chuyên gia kiên nhẫn, thời cơ

### 2. Hệ thống RAG thông minh

- Vector database với ChromaDB
- Vietnamese SBERT embeddings
- Retrieval Augmented Generation

### 3. Text-to-Speech

- Chuyển đổi phản hồi thành giọng nói
- Hỗ trợ nhiều giọng nói khác nhau

## 💬 Cách sử dụng Chat

1. **Chọn nhân vật** từ dropdown
2. **Nhập câu hỏi** của bạn
3. **Nhận lời khuyên** từ nhân vật dựa trên kinh nghiệm lịch sử

### Ví dụ câu hỏi:

- "Làm thế nào để trở thành một nhà lãnh đạo giỏi?"
- "Khi nào tôi nên hành động và khi nào nên chờ đợi?"
- "Làm sao để vượt qua thất bại?"
- "Cách xây dựng kế hoạch chiến lược?"

## 🛠 Phát triển

### Thêm nhân vật mới:

1. Tạo folder trong `backend/data/training/ten_nhan_vat/`
2. Thêm `personality.json` và `conversations.json`
3. Cập nhật `backend/app/models/characters.py`
4. Chạy `poetry run python scripts/setup_rag_system.py`

### API Endpoints:

- `GET /api/v1/characters/` - Lấy danh sách nhân vật
- `POST /api/v1/chat/advice` - Chat với nhân vật
- `GET /api/v1/characters/{id}` - Thông tin nhân vật

## 🐛 Troubleshooting

### Backend không khởi động:

- Kiểm tra port 8000 có bị chiếm không
- Chạy: `poetry install` để cài dependencies

### Frontend không kết nối:

- Đảm bảo backend đang chạy
- Kiểm tra URL API trong browser: http://localhost:8000/docs

### Lỗi Unicode:

- Set environment: `set PYTHONIOENCODING=utf-8`
- Restart terminal với admin privileges

## 📞 Hỗ trợ

Nếu gặp vấn đề, hãy:

1. Kiểm tra logs trong terminal
2. Xem API docs tại http://localhost:8000/docs
3. Test backend với `poetry run python backend/simple_test.py`

---

**🎉 Enjoy chatting with historical figures!** 🏺⚔️
