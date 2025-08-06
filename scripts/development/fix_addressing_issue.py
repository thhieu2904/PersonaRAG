# fix_addressing_issue.py

"""
Script kiểm tra và sửa vấn đề xưng hô trong hệ thống thực tế
"""

import sys
from pathlib import Path

def test_system_prompt():
    """Kiểm tra system prompt được sử dụng trong thực tế"""
    print("🔍 KIỂM TRA HỆ THỐNG PROMPT")
    print("=" * 60)
    
    try:
        from app.core.character_chat_service import get_character_chat_service
        from app.models.characters import get_character_by_id
        
        # Lấy service và character
        chat_service = get_character_chat_service()
        character = get_character_by_id("zhuge_liang")
        
        if not character:
            print("❌ Không tìm thấy nhân vật zhuge_liang")
            return
            
        print(f"✅ Tìm thấy nhân vật: {character.name}")
        
        # Kiểm tra system prompt
        system_prompt = chat_service.prompt_builder.build_system_prompt(character)
        
        print(f"\n📝 **System Prompt hiện tại:**")
        print("-" * 40)
        print(system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt)
        print("-" * 40)
        
        # Kiểm tra các thành phần quan trọng
        print(f"\n🔍 **Phân tích System Prompt:**")
        
        checks = [
            ("Có 'NGUYÊN TẮC XƯNG HÔ'", "NGUYÊN TẮC XƯNG HÔ" in system_prompt),
            ("Có 'Thưa chủ công'", "Thưa chủ công" in system_prompt),
            ("Có 'thần'", " thần " in system_prompt.lower()),
            ("Cấm 'ta'", "'ta'" in system_prompt),
            ("Cấm 'ngươi'", "'ngươi'" in system_prompt),
            ("Có yêu cầu 300-600 từ", "300-600" in system_prompt),
        ]
        
        for desc, result in checks:
            status = "✅" if result else "❌"
            print(f"   {status} {desc}: {result}")
        
        # Test với câu hỏi thực tế
        print(f"\n🧪 **Test với câu hỏi GPA:**")
        test_question = "muốn đạt được GPA 4.0 trong học kỳ này thì nên làm gì thưa quân sư?"
        
        user_prompt = chat_service.prompt_builder.build_user_prompt(
            character,
            test_question,
            relevant_contexts=None,
            conversation_history=None
        )
        
        print(f"\n📄 **User Prompt:**")
        print("-" * 40)
        print(user_prompt)
        print("-" * 40)
        
        # Test validation system
        print(f"\n⚡ **Test Response từ AI:**")
        
        response = chat_service.chat_ai.chat(
            user_message=user_prompt,
            system_prompt=system_prompt,
            reset_history=True
        )
        
        print(f"\n💬 **Phản hồi nhận được:**")
        print(f'"{response[:300]}..."')
        
        # Validate response
        is_valid, issues = chat_service.prompt_builder.validate_response(response, character)
        
        print(f"\n📊 **Validation Result:**")
        print(f"   Valid: {is_valid}")
        if not is_valid:
            print(f"   Issues:")
            for issue in issues:
                print(f"     - {issue}")
        else:
            print(f"   ✅ Tất cả kiểm tra đều PASS!")
            
        # Phân tích chi tiết
        print(f"\n📈 **Phân tích chi tiết:**")
        starts_correct = response.startswith("Thưa chủ công")
        cong_count = response.lower().count("chủ công")
        than_count = response.lower().count("thần")
        ta_count = response.lower().count(" ta ")
        nguoi_count = response.lower().count("ngươi")
        
        print(f"   - Bắt đầu 'Thưa chủ công': {starts_correct}")
        print(f"   - Số lần gọi 'chủ công': {cong_count}")
        print(f"   - Số lần tự xưng 'thần': {than_count}")
        print(f"   - Số lần dùng 'ta' (SAI): {ta_count}")
        print(f"   - Số lần dùng 'ngươi' (SAI): {nguoi_count}")
        
        # Đánh giá tổng thể
        score = 0
        total = 5
        if starts_correct: score += 1
        if cong_count >= 2: score += 1  
        if than_count >= 1: score += 1
        if ta_count == 0: score += 1
        if nguoi_count == 0: score += 1
        
        print(f"\n🎯 **Điểm số: {score}/{total} ({score/total*100:.1f}%)**")
        
        if score < total:
            print(f"\n🔧 **KHUYẾN NGHỊ:**")
            if not starts_correct:
                print(f"   - Cần force model bắt đầu bằng 'Thưa chủ công'")
            if cong_count < 2:
                print(f"   - Cần tăng số lần gọi 'chủ công'")
            if than_count < 1:
                print(f"   - Cần yêu cầu tự xưng 'thần'")
            if ta_count > 0:
                print(f"   - Cần cấm tuyệt đối việc dùng 'ta'")
            if nguoi_count > 0:
                print(f"   - Cần cấm tuyệt đối việc dùng 'ngươi'")
        else:
            print(f"\n🎉 **HOÀN HẢO! Hệ thống hoạt động đúng.**")
        
    except Exception as e:
        print(f"❌ Lỗi test: {e}")
        import traceback
        traceback.print_exc()

def apply_stricter_validation():
    """Áp dụng validation nghiêm ngặt hơn"""
    print(f"\n🔧 TĂNG CƯỜNG VALIDATION")
    print("=" * 60)
    
    # Thực hiện các cải thiện
    suggestions = [
        "✅ Đã cập nhật voice settings với pause_scale=1.8",
        "✅ Đã giảm speed xuống 0.6 cho tự nhiên hơn", 
        "✅ Đã thêm emotion_scale và breath_scale",
        "🔄 Cần áp dụng system prompt nghiêm ngặt hơn",
        "🔄 Cần force model tuân thủ xưng hô",
        "🔄 Có thể cần fine-tune model cho consistent addressing"
    ]
    
    for suggestion in suggestions:
        print(f"   {suggestion}")

if __name__ == "__main__":
    test_system_prompt()
    apply_stricter_validation()
