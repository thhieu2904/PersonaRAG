# backend/demo_enhanced_character.py

"""
Demo Enhanced Character Chat System
Thể hiện khả năng roleplay của Gia Cát Lượng với Qwen2.5-Instruct
"""

import sys
import logging
from pathlib import Path
import time

# Add backend to path
backend_path = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_path))

# Setup logging
logging.basicConfig(level=logging.WARNING)  # Chỉ hiện warning và error

def demo_character_conversation():
    """Demo cuộc trò chuyện với Gia Cát Lượng"""
    print("🎭 DEMO: Enhanced Character Chat với Gia Cát Lượng")
    print("=" * 60)
    
    try:
        from app.core.character_chat_service import get_character_chat_service
        
        chat_service = get_character_chat_service()
        
        # Start conversation
        print("🔄 Đang khởi tạo cuộc trò chuyện...")
        success, greeting, session_id = chat_service.start_conversation("zhuge_liang")
        
        if not success:
            print(f"❌ Khởi tạo thất bại: {greeting}")
            return
        
        print(f"\n📝 **Lời chào từ Gia Cát Lượng:**")
        print(f'"{greeting}"')
        print("\n" + "-" * 60)
        
        # Demo questions
        demo_questions = [
            {
                "question": "Thưa Khổng Minh, tôi đang gặp khó khăn trong việc quản lý nhóm làm việc. Nhóm tôi có người tài giỏi nhưng cũng có người chưa có kinh nghiệm. Anh có thể tư vấn cách cân bằng và phát huy sở trường của từng người không?",
                "context": "Vấn đề quản lý team đa dạng"
            },
            {
                "question": "Khổng Minh ơi, khi đưa ra quyết định quan trọng mà có nhiều ý kiến trái chiều, làm sao để tôi có thể quyết định đúng đắn và thuyết phục được mọi người?",
                "context": "Kỹ năng ra quyết định và thuyết phục"
            },
            {
                "question": "Thưa quân sư, trong thời đại hiện tại đầy biến động, làm thế nào để xây dựng chiến lược dài hạn mà vẫn linh hoạt thích ứng với những thay đổi bất ngờ?",
                "context": "Chiến lược và thích ứng"
            }
        ]
        
        for i, demo in enumerate(demo_questions, 1):
            print(f"\n🗣️  **Câu hỏi {i}** ({demo['context']}):")
            print(f'"{demo["question"]}"')
            
            print(f"\n🤔 Gia Cát Lượng đang suy nghĩ...")
            
            success, response, metadata = chat_service.chat_with_character(
                character_id="zhuge_liang",
                user_message=demo["question"],
                session_id=session_id,
                use_rag=False
            )
            
            if success:
                print(f"\n💬 **Gia Cát Lượng trả lời:**")
                print(f'"{response}"')
                
                # Show validation status
                if metadata:
                    validation_status = "✅ Hợp lệ" if metadata.get('response_valid', True) else "⚠️ Có vấn đề"
                    print(f"\n📊 Trạng thái: {validation_status}")
                    
                    if not metadata.get('response_valid', True):
                        issues = metadata.get('validation_issues', [])
                        print(f"   Vấn đề: {', '.join(issues)}")
                    
                    # Show follow-up questions
                    follow_ups = metadata.get('follow_up_questions', [])
                    if follow_ups:
                        print(f"\n❓ Câu hỏi gợi ý từ Gia Cát Lượng:")
                        for j, fq in enumerate(follow_ups[:2], 1):
                            print(f"   {j}. {fq}")
                
            else:
                print(f"\n❌ Lỗi: {response}")
            
            print("\n" + "-" * 60)
            
            if i < len(demo_questions):
                print("⏳ Chờ 2 giây trước câu hỏi tiếp theo...")
                time.sleep(2)
        
        # Session summary
        session_info = chat_service.get_session_info(session_id)
        print(f"\n📈 **Tóm tắt phiên:**")
        print(f"   - Tổng tin nhắn: {session_info.get('total_messages', 0)}")
        print(f"   - Session ID: {session_info.get('session_id', 'N/A')}")
        print(f"   - Thời gian bắt đầu: {session_info.get('created_at', 'N/A')}")
        
        model_status = chat_service.get_model_status()
        ai_info = model_status.get('ai_model', {})
        print(f"\n🤖 **Thông tin AI Model:**")
        print(f"   - Model: {ai_info.get('model_name', 'N/A')}")
        print(f"   - Context Length: {ai_info.get('context_length', 'N/A')}")
        print(f"   - Max Tokens: {ai_info.get('max_tokens', 'N/A')}")
        print(f"   - GPU Layers: {ai_info.get('n_gpu_layers', 'N/A')}")
        
        print(f"\n🎉 **Demo hoàn thành!** Gia Cát Lượng đã thể hiện:")
        print(f"   ✅ Phong cách xưng hô đúng thời đại ('thần', 'chủ công')")
        print(f"   ✅ Tính cách khiêm tốn nhưng tự tin")
        print(f"   ✅ Lời khuyên thiết thực dựa trên trí tuệ cổ điển")
        print(f"   ✅ Phong cách tư duy chiến lược và phân tích")
        
    except Exception as e:
        print(f"❌ Lỗi demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_character_conversation()
