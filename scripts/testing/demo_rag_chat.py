# backend/scripts/demo_rag_chat.py

"""
Demo script cho hệ thống RAG Chat
Tương tác với nhân vật lịch sử qua command line
"""

import sys
import asyncio
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(current_dir))

from app.models.characters import (
    Character, AdviceRequest, 
    get_character_by_id, get_all_characters
)
from app.core.prompt_builder import CharacterPromptBuilder


def display_welcome():
    """Display welcome message"""
    print("=" * 60)
    print("🏛️  CHÀO MỪNG ĐẾN HỘI ĐỒNG QUÂN SƯ RAG DEMO")
    print("=" * 60)
    print("Hệ thống tư vấn với các nhân vật lịch sử Việt Nam")
    print("Phiên bản: Demo (không cần vector database)")
    print()


def display_characters():
    """Display available characters"""
    print("📋 CÁC NHÂN VẬT CÓ SẴN:")
    print("-" * 40)
    
    characters = get_all_characters()
    for i, (char_id, character) in enumerate(characters.items(), 1):
        print(f"{i}. {character.name}")
        print(f"   ID: {char_id}")
        print(f"   Triều đại: {character.dynasty}")
        print(f"   Chuyên môn: {', '.join(character.expertise[:3])}...")
        print()


def select_character() -> Character:
    """Let user select a character"""
    characters = get_all_characters()
    char_list = list(characters.items())
    
    while True:
        try:
            choice = input("Chọn nhân vật (nhập số hoặc ID): ").strip()
            
            # Try by number
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(char_list):
                    return char_list[idx][1]
            
            # Try by ID
            character = get_character_by_id(choice)
            if character:
                return character
            
            print("❌ Lựa chọn không hợp lệ. Vui lòng thử lại.")
            
        except (ValueError, KeyboardInterrupt):
            print("\n👋 Tạm biệt!")
            sys.exit(0)


def simulate_rag_advice(character: Character, question: str) -> str:
    """Simulate RAG advice generation (without actual vector DB)"""
    builder = CharacterPromptBuilder()
    
    # Mock some relevant contexts based on character and question
    mock_contexts = []
    
    if character.id == "zhuge_liang":
        if any(keyword in question.lower() for keyword in ["lãnh đạo", "leader", "quản lý"]):
            mock_contexts.append({
                "content": "Gia Cát Lượng từng nói: 'Tận tâm tận lực, chết mà thôi'. Ông luôn nhấn mạnh rằng một người lãnh đạo phải gương mẫu và tận tâm với nhiệm vụ.",
                "metadata": {"story_id": "gc_007", "category": "leadership"},
                "similarity_score": 0.89,
                "rank": 1
            })
        elif any(keyword in question.lower() for keyword in ["kế hoạch", "chiến lược", "plan"]):
            mock_contexts.append({
                "content": "Trong 'Đối sách Lạc Dương', Gia Cát Lượng đã phân tích tình hình và đưa ra chiến lược 'Tam phân thiên hạ', cho thấy tầm quan trọng của việc phân tích kỹ lưỡng và lập kế hoạch dài hạn.",
                "metadata": {"story_id": "gc_002", "category": "strategy"},
                "similarity_score": 0.92,
                "rank": 1
            })
    
    elif character.id == "sima_yi":
        if any(keyword in question.lower() for keyword in ["kiên nhẫn", "chờ đợi", "thời cơ"]):
            mock_contexts.append({
                "content": "Tư Mã Ý đã kiên nhẫn chờ đợi nhiều năm dưới thời Tào Tháo, quan sát và học hỏi. Ông tin rằng 'Thời cơ không đến, tuyệt không hành động'.",
                "metadata": {"story_id": "sy_001", "category": "patience"},
                "similarity_score": 0.91,
                "rank": 1
            })
    
    # Build prompt
    prompt = builder.build_advice_prompt(
        character=character,
        user_question=question,
        relevant_contexts=mock_contexts,
        style="comprehensive"
    )
    
    # Simulate AI response (in real system, this would go to ChatAI)
    advice = generate_mock_advice(character, question, mock_contexts)
    
    return advice


def generate_mock_advice(character: Character, question: str, contexts: list) -> str:
    """Generate mock advice based on character personality"""
    
    if character.id == "zhuge_liang":
        if "lãnh đạo" in question.lower() or "leader" in question.lower():
            return f"""Như {character.name}, tôi hiểu rằng lãnh đạo không chỉ là chức vụ mà là trách nhiệm.

Từ kinh nghiệm phụ tá Lưu Bị, tôi nhận thấy:

1. **Gương mẫu đi trước**: "Tận tâm tận lực, chết mà thôi" - một người lãnh đạo phải làm gương cho người khác nối theo.

2. **Lắng nghe và học hỏi**: Sau thất bại ở Nhai Đình, tôi đã học được rằng không được chủ quan, luôn phải lắng nghe ý kiến của đồng đội.

3. **Tầm nhìn dài hạn**: Như trong "Đối s책 Lạc Dương", hãy có chiến lược rõ ràng và kiên trì thực hiện từng bước.

4. **Quan tâm đến người dưới**: "Dân vi quý, xã tắc thứ chi, quân vi khinh" - người lãnh đạo phải đặt lợi ích tập thể lên trước.

Hãy nhớ: không có việc gì nhỏ, chỉ có việc được làm tốt hay không. Mỗi quyết định của bạn đều ảnh hưởng đến cả tập thể."""

        elif "kế hoạch" in question.lower() or "chiến lược" in question.lower():
            return f"""Là {character.name}, tôi luôn tin rằng "biết người biết ta, trăm trận trăm thắng".

Quy trình lập kế hoạch của tôi:

1. **Phân tích tình hình**: 
   - Đánh giá thế mạnh và yếu điểm của mình
   - Phân tích cơ hội và thách thức
   - Hiểu rõ nguồn lực hiện có

2. **Xây dựng chiến lược**:
   - Đặt mục tiêu rõ ràng
   - Chia nhỏ thành các bước cụ thể
   - Chuẩn bị phương án dự phòng

3. **Thực hiện linh hoạt**:
   - Theo dõi tiến độ thường xuyên
   - Sẵn sàng điều chỉnh khi cần
   - Học hỏi từ mỗi bước đi

Nhớ rằng: kế hoạch tốt nhất là kế hoạch có thể thay đổi khi tình hình thay đổi, nhưng mục tiêu cuối cùng vẫn không đổi."""

    elif character.id == "sima_yi":
        if "kiên nhẫn" in question.lower() or "thời cơ" in question.lower():
            return f"""Như {character.name}, tôi đã học được rằng "kiên nhẫn là vũ khí mạnh nhất của kẻ thông thái".

Triết lý của tôi về thời cơ:

1. **Quan sát và chờ đợi**:
   - Không vội vàng hành động khi chưa chín muồi
   - Dành thời gian quan sát và học hỏi
   - Chuẩn bị kỹ lưỡng cho cơ hội

2. **Nhận biết thời điểm đúng**:
   - Khi đối thủ yếu nhất
   - Khi mình mạnh nhất
   - Khi điều kiện khách quan thuận lợi

3. **Hành động quyết đoán**:
   - Một khi đã quyết định, hành động nhanh chóng
   - Không do dự hay lưỡng lự
   - Tận dụng tối đa lợi thế

Trong cuộc đời, có những lúc cần kiên nhẫn chờ đợi, có những lúc cần hành động mạnh mẽ. Nghệ thuật nằm ở việc biết phân biệt hai thời điểm này.

Hãy nhớ: "Thời cơ không đến, tuyệt không hành động. Thời cơ đã đến, tuyệt không do dự"."""

    # Default response
    return f"""Là {character.name}, tôi hiểu câu hỏi của bạn về "{question}".

Dựa trên kinh nghiệm của mình, tôi muốn chia sẻ:

{character.advice_style}

Một số nguyên tắc tôi luôn tuân theo:
{chr(10).join(f'- {trait}' for trait in character.personality_traits[:3])}

Như tôi thường nói: "{character.famous_quotes[0] if character.famous_quotes else 'Hãy luôn học hỏi và cải thiện bản thân'}"

Hy vọng những suy nghĩ này có thể giúp ích cho bạn."""


def chat_session(character: Character):
    """Main chat session"""
    print(f"\n💬 CUỘC TRÒ CHUYỆN VỚI {character.name.upper()}")
    print("=" * 60)
    
    # Character introduction
    builder = CharacterPromptBuilder()
    intro = builder.build_character_introduction(character)
    print(f"🎭 {character.name}: {intro}")
    print()
    print("Bạn có thể hỏi tôi về lãnh đạo, chiến lược, hay bất cứ điều gì bạn muốn tham khảo.")
    print("Gõ 'quit' hoặc 'exit' để kết thúc.")
    print("-" * 60)
    
    conversation_count = 0
    
    while True:
        try:
            # Get user input
            question = input(f"\n🙋 Bạn: ").strip()
            
            if not question:
                continue
                
            if question.lower() in ['quit', 'exit', 'thoát', 'bye']:
                print(f"\n🎭 {character.name}: Cảm ơn bạn đã trò chuyện. Chúc bạn thành công!")
                break
            
            # Show thinking
            print(f"\n🤔 {character.name} đang suy nghĩ...")
            
            # Generate advice
            advice = simulate_rag_advice(character, question)
            
            # Display response
            print(f"\n🎭 {character.name}:")
            print("-" * 40)
            print(advice)
            
            conversation_count += 1
            
            # Suggest follow-up after a few exchanges
            if conversation_count % 3 == 0:
                follow_ups = builder.generate_follow_up_questions(character, advice)
                if follow_ups:
                    print(f"\n💡 {character.name} gợi ý: {follow_ups[0]}")
            
        except KeyboardInterrupt:
            print(f"\n\n👋 {character.name}: Tạm biệt và chúc bạn may mắn!")
            break
        except Exception as e:
            print(f"\n❌ Có lỗi xảy ra: {e}")


def main():
    """Main function"""
    display_welcome()
    
    try:
        # Show available characters
        display_characters()
        
        # Let user select character
        character = select_character()
        
        print(f"\n✅ Đã chọn: {character.name}")
        print(f"📖 {character.description}")
        
        # Start chat session
        chat_session(character)
        
    except KeyboardInterrupt:
        print("\n\n👋 Cảm ơn bạn đã sử dụng Hội đồng Quân sư!")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")


if __name__ == "__main__":
    main()
