# PersonaRAG v3 🎭

**AI Character Chat System với RAG Integration & Vietnamese TTS**

## 🌟 Overview

PersonaRAG v3 là hệ thống chat AI cho phép tương tác với các nhân vật lịch sử thông qua RAG (Retrieval-Augmented Generation) và TTS. Hệ thống sử dụng Qwen2.5-7B-Instruct được tối ưu cho RTX 3060 6GB với ChromaDB vector database và Vietnamese embeddings.

## ✨ Core Features

### 🤖 **AI Character System**

- **Gia Cát Lượng** & **Tư Mã Ý** personas với modern life advisor role
- **Advanced Prompt Builder** tối ưu cho character consistency
- **Character addressing**: Nhân vật gọi user là "chủ công"
- **RAG-enhanced responses** dựa trên historical knowledge

### 🧠 **RAG Integration**

- **ChromaDB** vector database với 18+ character stories
- **Vietnamese sentence embeddings** (`keepitreal/vietnamese-sbert`)
- **Context retrieval** cho relevant historical examples
- **Modern life application** của ancient wisdom

### 🎯 **Technical Stack**

- **Backend**: FastAPI + Poetry + ChromaDB + llama-cpp-python
- **Frontend**: React + Vite + Modern UI components
- **AI Model**: Qwen2.5-7B-Instruct GGUF Q4_K_M
- **TTS**: F5-TTS Vietnamese integration ready
- **Database**: Vector store + JSON training data

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- RTX 3060 6GB+ (recommended)
- 16GB+ RAM

### Backend Setup

```bash
cd backend/
poetry install
poetry run python start_server.py
```

### Frontend Setup

```bash
cd frontend/
npm install
npm run dev
```

### Full Stack

```bash
# Windows
scripts\deployment\start_full_stack.bat
```

## 📊 Project Status

### ✅ Implemented

- [x] RAG system với ChromaDB
- [x] Character AI với Qwen2.5-7B
- [x] API endpoints với FastAPI
- [x] Modern advisor personas
- [x] RTX 3060 optimization
- [x] Vietnamese embeddings
- [x] Test suite comprehensive

### 🎯 Ready for Development

- [ ] Frontend UI completion
- [ ] More character personas
- [ ] TTS voice synthesis
- [ ] User authentication
- [ ] Conversation history
- [ ] Mobile responsive UI

## 📁 Project Structure

```
PersonaRAG_v3/
├── 📄 README.md (this file)
├── 📄 PROJECT_STRUCTURE.md (detailed structure)
├── 📄 CLEANUP_SUMMARY.md (recent cleanup info)
│
├── 🏢 backend/ (Core FastAPI application)
├── 🌐 frontend/ (React web application)
├── 📚 docs/ (Documentation & guides)
├── 🛠️ scripts/ (Testing, development & deployment)
└── 🐳 nginx/ (Reverse proxy config)
```

## 🧪 Testing

```bash
# Test RAG integration
poetry run python scripts/testing/test_complete_rag.py

# Test character chat
poetry run python scripts/testing/test_enhanced_chat.py

# Quick validation
poetry run python scripts/testing/quick_rag_test.py
```

## 📖 Documentation

- **[Setup Guide](docs/setup/)** - Installation & configuration
- **[API Documentation](docs/API.md)** - REST API reference
- **[RAG Guide](docs/guides/RAG_README.md)** - Vector database setup
- **[TTS Guide](docs/guides/TTS_README.md)** - Voice synthesis
- **[Development Docs](docs/development/)** - Technical details

## 🎮 Usage Examples

### Basic Chat

```python
# Start conversation
POST /api/v1/chat/start
{
  "character_name": "gia_cat_luong"
}

# Send message
POST /api/v1/chat/
{
  "message": "Tôi gặp khó khăn trong quản lý team",
  "character_name": "gia_cat_luong",
  "session_id": "...",
  "use_rag": true
}
```

### RAG Context Example

```
User: "Làm sao để trở thành leader giỏi?"
RAG retrieves: "Tam cố thảo lư", "Quản lý Thành Đô"
Response: "Thưa chủ công, [wisdom from historical contexts]..."
```

## 🛠️ Development

### Add New Character

1. Define persona in `app/core/advanced_prompt_builder.py`
2. Add training data in `data/training/[character]/`
3. Run RAG setup: `poetry run python scripts/setup_rag_system.py`

### Run Development Server

```bash
cd backend/
poetry run uvicorn app.main:app --reload --port 8000
```

## 🐳 Deployment

### Docker

```bash
docker-compose up -d
```

### Production

```bash
scripts/deployment/start_full_stack.bat
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Qwen2.5 Team** - Outstanding instruction-following model
- **ChromaDB** - Excellent vector database
- **llama-cpp-python** - Efficient GGUF inference
- **F5-TTS** - High-quality Vietnamese TTS
- **Community** - Testing and feedback

---

**⭐ Star this repository if you find it useful!**

**📧 Contact**: [Your Email] | **🐛 Issues**: [GitHub Issues](../../issues)
