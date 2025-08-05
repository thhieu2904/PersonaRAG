# Testing Scripts

Thư mục chứa các script test và validation cho hệ thống PersonaRAG.

## Quick Tests

- `quick_rag_test.py` - Test nhanh RAG system
- `quick_setup.py` - Setup nhanh hệ thống
- `quick_test_character.py` - Test nhanh character system

## Simple Tests

- `simple_chat_test.py` - Test đơn giản chat functionality
- `simple_test.py` - Test cơ bản

## Full Integration Tests

- `test_complete_rag.py` - Test toàn bộ RAG integration
- `test_rag_working.py` - Test RAG system hoạt động
- `test_rag_fixes.py` - Test các fixes cho RAG

## Character & Chat Tests

- `test_enhanced_chat.py` - Test enhanced chat system
- `test_modern_advisor.py` - Test modern advisor functionality

## API Tests

- `test_api_rag.py` - Test API với RAG integration

## Frontend Tests

- `test_frontend.py` - Test frontend integration

## Cách sử dụng

```bash
# Chạy từ backend directory
cd backend
poetry run python ../scripts/testing/[script_name].py

# Hoặc với absolute path
poetry run python "d:\Personal\PersonaRAG_v3\scripts\testing\[script_name].py"
```

## Dependencies

Các script này require backend environment đã được setup với Poetry.
