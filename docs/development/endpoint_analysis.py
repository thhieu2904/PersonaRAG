# endpoint_analysis.py

"""
Phân tích và tài liệu hóa tất cả endpoint trong hệ thống PersonaRAG
"""

import sys
from pathlib import Path

def analyze_endpoints():
    """Phân tích tất cả endpoint trong hệ thống"""
    print("🔍 PHÂN TÍCH ENDPOINT SYSTEM")
    print("=" * 80)
    
    endpoints = {
        "CORE API ENDPOINTS": {
            "/": {
                "method": "GET",
                "file": "main.py",
                "purpose": "Health check endpoint gốc",
                "description": "Kiểm tra service có hoạt động không"
            }
        },
        
        "CHAT ENDPOINTS - Character Chat System": {
            "/api/v1/chat/": {
                "method": "POST", 
                "file": "api/v1/chat.py",
                "purpose": "🎭 ENDPOINT CHÍNH cho chat với nhân vật",
                "description": "Chat với AI character sử dụng GGUF model + RAG enhanced",
                "features": [
                    "✅ Advanced prompt validation (chủ công/thần)", 
                    "✅ Session management",
                    "✅ RAG integration optional",
                    "✅ Character-specific personality",
                    "✅ Full conversation context"
                ],
                "request": "ChatRequest(message, character_name, session_id, use_rag)",
                "response": "ChatResponse(response, success, session_id, metadata)"
            },
            "/api/v1/chat/start": {
                "method": "POST",
                "file": "api/v1/chat.py", 
                "purpose": "Khởi tạo conversation session",
                "description": "Tạo session mới và lời chào từ character"
            }
        },
        
        "RAG ENDPOINTS - Knowledge-Based Chat": {
            "/api/v1/rag/advice": {
                "method": "POST",
                "file": "api/v1/rag.py",
                "purpose": "🧠 ENDPOINT TƯ VẤN sử dụng RAG",
                "description": "Tư vấn nhanh dựa trên knowledge base + character personality",
                "features": [
                    "✅ RAG-powered responses",
                    "✅ Quick advice format", 
                    "✅ Knowledge base search",
                    "✅ Character personality maintained",
                    "✅ Recently updated với advanced prompt validation"
                ],
                "request": "AdviceRequest(question, character_id, context)",
                "response": "AdviceResponse(advice, sources, confidence)",
                "use_case": "Frontend sử dụng cho quick advice"
            },
            "/api/v1/rag/search": {
                "method": "POST",
                "file": "api/v1/rag.py",
                "purpose": "Tìm kiếm context từ knowledge base",
                "description": "Search relevant information cho câu hỏi"
            },
            "/api/v1/rag/characters": {
                "method": "GET",
                "file": "api/v1/rag.py",
                "purpose": "List available characters",
                "description": "Danh sách nhân vật có sẵn trong system"
            },
            "/api/v1/rag/knowledge-base/initialize": {
                "method": "POST",
                "file": "api/v1/rag.py", 
                "purpose": "Khởi tạo knowledge base",
                "description": "Setup vector database với character data"
            }
        },
        
        "AI CHAT ENDPOINTS - Direct Model Access": {
            "/api/v1/ai/chat": {
                "method": "POST",
                "file": "api/v1/chat_ai.py",
                "purpose": "🤖 Direct AI model chat",
                "description": "Chat trực tiếp với GGUF model không qua character layer",
                "features": [
                    "🔧 Model configuration",
                    "🔧 Custom system prompts", 
                    "🔧 Streaming support",
                    "🔧 History management"
                ],
                "use_case": "Development và testing AI model"
            },
            "/api/v1/ai/chat/stream": {
                "method": "POST",
                "file": "api/v1/chat_ai.py",
                "purpose": "Streaming AI responses",
                "description": "Real-time streaming cho responses dài"
            },
            "/api/v1/ai/configure": {
                "method": "POST",
                "file": "api/v1/chat_ai.py",
                "purpose": "Configure AI model parameters",
                "description": "Thay đổi temperature, max_tokens, etc."
            }
        },
        
        "VOICE/TTS ENDPOINTS": {
            "/api/v1/voice/setup-character-voice": {
                "method": "POST",
                "file": "api/v1/voice.py",
                "purpose": "Setup giọng nói cho character",
                "description": "Upload và configure voice samples"
            },
            "/api/v1/voice/generate-speech": {
                "method": "POST", 
                "file": "api/v1/voice.py",
                "purpose": "Tạo speech từ text",
                "description": "Text-to-speech với character voice"
            },
            "/api/v1/voice/characters": {
                "method": "GET",
                "file": "api/v1/voice.py",
                "purpose": "List characters có voice",
                "description": "Danh sách character đã setup voice"
            }
        },
        
        "TTS OPTIMIZED ENDPOINTS": {
            "/api/v1/tts/synthesize": {
                "method": "POST",
                "file": "api/v1/tts_optimized.py", 
                "purpose": "🎵 TTS synthesis optimized",
                "description": "Optimized F5-TTS synthesis với improved settings",
                "features": [
                    "✅ Enhanced voice settings (emotion, breath)",
                    "✅ Batch processing",
                    "✅ Caching",
                    "✅ Performance monitoring"
                ]
            },
            "/api/v1/tts/synthesize-batch": {
                "method": "POST",
                "file": "api/v1/tts_optimized.py",
                "purpose": "Batch TTS processing",
                "description": "Process multiple texts cùng lúc"
            },
            "/api/v1/tts/stats": {
                "method": "GET", 
                "file": "api/v1/tts_optimized.py",
                "purpose": "TTS performance statistics",
                "description": "Monitor TTS service performance"
            }
        }
    }
    
    print("\n📋 **ENDPOINT COMPARISON: /chat vs /rag/advice**")
    print("=" * 80)
    
    comparison = {
        "Purpose": {
            "/api/v1/chat/": "Full conversation với character personality",
            "/api/v1/rag/advice": "Quick advice với RAG knowledge"
        },
        "Use Case": {
            "/api/v1/chat/": "Interactive chat session, roleplay",
            "/api/v1/rag/advice": "Quick Q&A, knowledge lookup"
        },
        "Session Management": {
            "/api/v1/chat/": "✅ Full session với history",
            "/api/v1/rag/advice": "❌ Stateless, no session"
        },
        "Response Style": {
            "/api/v1/chat/": "Conversational, contextual",
            "/api/v1/rag/advice": "Direct advice format"
        },
        "RAG Integration": {
            "/api/v1/chat/": "Optional (use_rag parameter)",
            "/api/v1/rag/advice": "Always enabled"
        },
        "Performance": {
            "/api/v1/chat/": "Slower (full conversation processing)",
            "/api/v1/rag/advice": "Faster (focused advice)"
        },
        "Frontend Usage": {
            "/api/v1/chat/": "Main chat interface",
            "/api/v1/rag/advice": "Quick advice widgets, suggestions"
        }
    }
    
    for aspect, details in comparison.items():
        print(f"\n**{aspect}:**")
        for endpoint, desc in details.items():
            print(f"   {endpoint}")
            print(f"     → {desc}")
    
    print(f"\n🎯 **LÝ DO CÓ 2 ENDPOINT CHAT:**")
    print("=" * 80)
    
    reasons = [
        "🎭 **Separation of Concerns:**",
        "   - /chat/: Full interactive conversation system",
        "   - /rag/advice: Specialized knowledge-based Q&A",
        "",
        "🚀 **Performance Optimization:**", 
        "   - /chat/: Heavy processing với session management",
        "   - /rag/advice: Lightweight cho quick responses",
        "",
        "🎨 **Frontend Flexibility:**",
        "   - Chat widget sử dụng /chat/ cho conversation",
        "   - Advice panels sử dụng /rag/advice cho suggestions",
        "",
        "🔧 **Different Processing Pipelines:**",
        "   - /chat/: Character → Session → AI → Validation → Response",
        "   - /rag/advice: Question → RAG Search → Character Filter → Advice",
        "",
        "📱 **User Experience:**",
        "   - /chat/: Immersive roleplay experience",
        "   - /rag/advice: Quick help và productivity focus"
    ]
    
    for reason in reasons:
        print(reason)
    
    print(f"\n💡 **BEST PRACTICES:**")
    print("=" * 80)
    
    practices = [
        "✅ Use /chat/ cho main conversation interface",
        "✅ Use /rag/advice cho quick help features", 
        "✅ Frontend có thể combine cả hai cho rich UX",
        "✅ /chat/ cho social/emotional interaction",
        "✅ /rag/advice cho practical/factual queries",
        "✅ Monitor both endpoints cho performance optimization"
    ]
    
    for practice in practices:
        print(f"   {practice}")
    
    # Display detailed endpoints
    print(f"\n📚 **CHI TIẾT TẤT CẢ ENDPOINTS:**")
    print("=" * 80)
    
    for category, endpoints_list in endpoints.items():
        print(f"\n🔸 **{category}**")
        print("-" * 60)
        
        for endpoint, details in endpoints_list.items():
            print(f"\n   {details['method']} {endpoint}")
            print(f"   📁 File: {details['file']}")
            print(f"   🎯 Purpose: {details['purpose']}")
            print(f"   📝 Description: {details['description']}")
            
            if 'features' in details:
                print(f"   ✨ Features:")
                for feature in details['features']:
                    print(f"      {feature}")
            
            if 'request' in details:
                print(f"   📤 Request: {details['request']}")
            
            if 'response' in details:
                print(f"   📥 Response: {details['response']}")
            
            if 'use_case' in details:
                print(f"   💼 Use Case: {details['use_case']}")

if __name__ == "__main__":
    analyze_endpoints()
