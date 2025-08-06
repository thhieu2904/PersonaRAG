# Testing Scripts

Thư mục chứa các script test và validation cho hệ thống PersonaRAG.

## Core Tests (Essential)

- `test_api.py` - Test REST API endpoints
- `test_full_rag_integration.py` - Test toàn bộ RAG integration
- `test_full_system.py` - Test complete system functionality
- `test_rag_simple.py` - Test RAG system basics

## Quick Tests

- `quick_rag_test.py` - Test nhanh RAG system
- `quick_setup.py` - Setup nhanh hệ thống
- `quick_test.py` - Test nhanh general functionality
- `quick_test_character.py` - Test nhanh character system

## Demo & Development

- `demo_rag_chat.py` - Demo RAG chat functionality
- `simple_chat_test.py` - Test đơn giản chat functionality
- `simple_test.py` - Test cơ bản

## Specialized Tests

- `test_frontend.py` - Test frontend integration
- `test_ttsnorm.py` - Test TTS normalization

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
