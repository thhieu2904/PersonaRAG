# PersonaRAG v3 - Clean Project Structure

## 📁 Project Overview

```
PersonaRAG_v3/
├── 📄 README.md                    # Main project documentation
├── 📄 NEXT_STEPS.md                # Roadmap và next features
├── 📄 docker-compose.yml           # Docker orchestration
├── 📄 .gitignore                   # Git ignore rules
│
├── 📁 backend/                     # ✨ CORE APPLICATION
│   ├── 📁 app/                     # Main application code
│   │   ├── 📁 api/                 # FastAPI routes & endpoints
│   │   ├── 📁 core/                # Core business logic
│   │   ├── 📁 models/              # Data models & schemas
│   │   ├── 📁 database/            # Database configurations
│   │   └── 📁 utils/               # Utility functions
│   ├── 📁 data/                    # Application data
│   │   ├── 📁 training/            # Character training data
│   │   ├── 📁 chroma_db/           # Vector database
│   │   └── 📁 audio_samples/       # Audio files
│   ├── 📁 models/                  # AI model storage
│   ├── 📁 logs/                    # Application logs
│   ├── 📁 scripts/                 # Backend utility scripts
│   ├── 📁 tests/                   # Unit tests
│   ├── 📁 configs/                 # Configuration files
│   ├── 📄 pyproject.toml           # Poetry dependencies
│   ├── 📄 requirements.txt         # Main dependencies
│   └── 📄 start_server.py          # Server entry point
│
├── 📁 frontend/                    # React.js web application
│   ├── 📁 src/                     # Source code
│   ├── 📁 public/                  # Static assets
│   ├── 📄 package.json             # Node.js dependencies
│   └── 📄 vite.config.js           # Vite configuration
│
├── 📁 docs/                        # 📚 DOCUMENTATION
│   ├── 📁 guides/                  # User & API guides
│   │   ├── 📄 CHAT_AI_README.md    # Chat AI guide
│   │   ├── 📄 RAG_README.md        # RAG system guide
│   │   └── 📄 TTS_README.md        # TTS integration
│   ├── 📁 development/             # Development docs
│   │   ├── 📄 RAG_INTEGRATION_COMPLETE.md
│   │   ├── 📄 ENHANCEMENT_SUMMARY.md
│   │   └── 📄 *_FIX_*.md           # Fix documentation
│   └── 📁 setup/                   # Setup instructions
│
├── 📁 scripts/                     # 🛠️ UTILITY SCRIPTS
│   ├── 📁 testing/                 # Test scripts
│   │   ├── 📄 test_complete_rag.py # Full RAG integration test
│   │   ├── 📄 test_rag_*.py        # RAG-specific tests
│   │   ├── 📄 quick_*.py           # Quick validation tests
│   │   └── 📄 simple_*.py          # Basic functionality tests
│   ├── 📁 development/             # Development tools
│   │   ├── 📄 demo_*.py            # Demo scripts
│   │   └── 📄 fix_*.py             # Data fixing scripts
│   └── 📁 deployment/              # Production deployment
│       └── 📄 start_full_stack.bat # Windows deployment script
│
└── 📁 nginx/                       # Reverse proxy configuration
    └── 📄 nginx.conf
```

## 🚀 Core Features Status

### ✅ Implemented & Working

- **RAG System**: ChromaDB + Vietnamese embeddings
- **Character AI**: Qwen2.5-7B-Instruct với character personas
- **API Layer**: FastAPI với RAG-enhanced endpoints
- **Advanced Prompt Builder**: Optimized cho RTX 3060 6GB
- **TTS Integration**: F5-TTS Vietnamese ready

### 🎯 Ready for Development

- **Frontend**: React.js foundation setup
- **Database**: Character knowledge base populated
- **Testing**: Comprehensive test suite
- **Documentation**: Complete guides available

## 📝 Quick Start Commands

```bash
# Backend development
cd backend
poetry install
poetry run python start_server.py

# Frontend development
cd frontend
npm install
npm run dev

# Run tests
poetry run python ../scripts/testing/test_complete_rag.py

# Full stack deployment
scripts/deployment/start_full_stack.bat
```

## 🔧 Development Workflow

1. **Feature Development**: Work in `backend/app/` or `frontend/src/`
2. **Testing**: Use scripts from `scripts/testing/`
3. **Documentation**: Update docs in `docs/`
4. **Configuration**: Modify `backend/configs/`

## 📊 Current Tech Stack

- **Backend**: FastAPI + Poetry + ChromaDB + llama-cpp-python
- **Frontend**: React + Vite + Modern UI
- **AI**: Qwen2.5-7B-Instruct GGUF + Vietnamese embeddings
- **Database**: ChromaDB vector store + JSON data
- **Deployment**: Docker + nginx reverse proxy

---

**Project Status**: ✅ Core features implemented, ready for next development phase
