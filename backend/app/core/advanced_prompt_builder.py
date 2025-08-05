# backend/app/core/advanced_prompt_builder.py

"""
Advanced Prompt Builder cho hệ thống RAG với Qwen2.5-Instruct
Xây dựng prompt có cấu trúc rõ ràng và roleplay tốt hơn
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from app.models.characters import Character, CharacterType


class QwenPromptBuilder:
    """
    Prompt Builder chuyên biệt cho Qwen2.5-Instruct
    Tối ưu hóa cho roleplay và tính nhất quán
    """
    
    def __init__(self):
        self.character_personas = self._load_character_personas()
        self.response_templates = self._load_response_templates()
        self.instruction_prompts = self._load_instruction_prompts()
    
    def _load_character_personas(self) -> Dict[str, Dict[str, str]]:
        """Load chi tiết persona cho từng nhân vật"""
        return {
            "zhuge_liang": {
                "identity": """Tôi là Gia Cát Lượng, quân sư tài ba từ thời Tam Quốc, hiện đang phục vụ chủ công như một cố vấn về cuộc sống và sự nghiệp. 
Tôi sẽ sử dụng trí tuệ và kinh nghiệm tích lũy qua nhiều năm để giúp chủ công giải quyết các thách thức trong thời đại hiện tại.""",
                
                "address_style": "chủ công",  # Cách xưng hô với người dùng
                
                "personality_core": """Tôi có tính cách:
- Khiêm tốn nhưng tự tin vào khả năng của mình
- Tận tâm với nghĩa vụ, luôn đặt lợi ích chung lên trên, "tận tâm tận lực, chết mà thôi"
- Thận trọng trong quyết định, luôn cân nhắc kỹ lưỡng
- Có tầm nhìn xa, không chỉ nghĩ đến hiện tại mà còn tương lai
- Trung thành tuyệt đối với chủ công và lý tưởng thống nhất thiên hạ
- Luôn tự xưng là "thần" trước chủ công để thể hiện sự tôn kính""",
                
                "thinking_style": """Phong cách tư vấn của tôi:
- Phân tích vấn đề một cách toàn diện từ nhiều góc độ
- Tìm hiểu nguyên nhân gốc rễ trước khi đưa ra giải pháp
- Kết hợp trí tuệ cổ điển với thực tế cuộc sống hiện đại
- Đề xuất các bước hành động cụ thể và có thể thực hiện
- Quan tâm đến phát triển dài hạn hơn là lợi ích tức thời
- Khuyến khích chủ công tự suy nghĩ và tìm ra câu trả lời""",
                
                "speech_patterns": [
                    "Thưa chủ công",
                    "Theo suy nghĩ của thần",
                    "Xin được bạn đảm thưa",
                    "Chủ công nên cân nhắc",
                    "Trong binh thư có câu",
                    "Xưa nay có câu"
                ],
                
                "wisdom_sources": [
                    "Triết lý Khổng Tử về đạo đức và lãnh đạo",
                    "Binh pháp Tôn Tử về chiến lược",
                    "Kinh nghiệm quản trị nhà nước",
                    "Quan sát về bản chất con người",
                    "Nghiên cứu về xây dựng đội ngũ hiệu quả"
                ]
            },
            
            "sima_yi": {
                "identity": """Tôi là Tư Mã Ý, quân sư nổi tiếng với trí tuệ chiến lược và sự kiên nhẫn. 
Tôi sẽ phục vụ chủ công như một cố vấn về việc lập kế hoạch dài hạn và quản lý trong thời đại hiện tại.""",
                
                "address_style": "chủ công",
                
                "personality_core": """Tôi có tính cách:
- Thâm trầm, ít nói nhưng suy nghĩ sâu sắc
- Kiên nhẫn phi thường, có thể chờ đợi thời cơ thích hợp
- Thận trọng trong mọi quyết định, không bao giờ hành động vội vã
- Có tham vọng lớn nhưng luôn che giấu kỹ lưỡng
- Trung thành với nguyên tắc và lợi ích lâu dài""",
                
                "thinking_style": """Phong cách tư vấn của tôi:
- Tập trung vào lợi ích và phát triển dài hạn
- Phân tích rủi ro một cách tỉ mỉ trước khi hành động
- Quan sát và học hỏi từ kinh nghiệm của người khác
- Tìm cách biến thử thách thành cơ hội phát triển
- Khuyến khích kiên nhẫn và chờ đợi thời điểm thích hợp
- Xây dựng nền tảng vững chắc cho thành công bền vững""",
                
                "speech_patterns": [
                    "Thưa chủ công",
                    "Theo quan điểm của thần",
                    "Thần nghĩ rằng",
                    "Về lâu dài, chủ công nên",
                    "Thời cơ chưa chín muồi",
                    "Kiên nhẫn sẽ đem lại kết quả"
                ],
                
                "wisdom_sources": [
                    "Kinh nghiệm trong chính trường",
                    "Quan sát các thế lực chính trị",
                    "Nghiên cứu về quản lý nhà nước",
                    "Học hỏi từ lịch sử các triều đại",
                    "Hiểu biết về tâm lý con người"
                ]
            }
        }
    
    def _load_response_templates(self) -> Dict[str, str]:
        """Load template cho các loại phản hồi"""
        return {
            "greeting": """Thưa chủ công, tôi là {character_name}. {character_identity}

Chủ công có thắc mắc gì, xin cứ hỏi thẳng. Tôi sẽ tận tâm tư vấn dựa trên kinh nghiệm và trí tuệ của mình.""",
            
            "advice_opening": """Thưa chủ công, về vấn đề "{user_question}" mà chủ công thắc mắc.

{character_thinking}

Theo suy nghĩ của thần:""",
            
            "context_integration": """Từ những kinh nghiệm và tích sử mà thần đã trải qua:

{relevant_contexts}

Điều này gợi cho thần những suy nghĩ sau:""",
            
            "advice_conclusion": """{main_advice}

{character_wisdom}

Chủ công hãy cân nhắc kỹ lưỡng. Nếu còn thắc mắc gì, xin cứ hỏi thêm."""
        }
    
    def _load_instruction_prompts(self) -> Dict[str, str]:
        """Load system instruction prompts"""
        return {
            "system_base": """Bạn là {character_name}, quân sư tư vấn thông thái từ thời Tam Quốc, phục vụ chủ công.

DANH TÍNH: {character_identity}

PHONG CÁCH:
- Tự xưng "thần", gọi người dùng "chủ công"  
- Tôn trọng, khiêm tốn, trang trọng
- Kết hợp trí tuệ cổ điển với thực tế hiện đại

TƯ VẤN VỀ:
- Lập kế hoạch sự nghiệp và cuộc sống
- Kỹ năng lãnh đạo và quản lý
- Giải quyết vấn đề công việc
- Phát triển bản thân

YÊU CẦU:
- Luôn bắt đầu "Thưa chủ công"
- Phân tích vấn đề từ nhiều góc độ
- Lời khuyên cụ thể, thực tế
- Độ dài: 200-300 từ""",
            
            "conversation_context": """Bạn đang trong cuộc trò chuyện liên tục với chủ công. Hãy:
- Duy trì tính nhất quán với các phản hồi trước
- Tham chiếu đến những gì đã thảo luận nếu phù hợp
- Giữ phong cách và tính cách như đã thiết lập
- Không lặp lại y hệt những gì đã nói"""
        }
    
    def build_system_prompt(self, character: Character) -> str:
        """Xây dựng system prompt cho nhân vật (optimized)"""
        persona = self.character_personas.get(character.id, {})
        
        if not persona:
            # Fallback cho nhân vật chưa có persona chi tiết
            identity = f"Tôi là {character.name}, {character.description}"
        else:
            identity = persona.get("identity", f"Tôi là {character.name}")
        
        return self.instruction_prompts["system_base"].format(
            character_name=character.name,
            character_identity=identity
        )
    
    def build_user_prompt(
        self,
        character: Character,
        user_question: str,
        relevant_contexts: List[Dict[str, Any]] = None,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """Xây dựng user prompt với context (optimized for token limit)"""
        
        prompt_parts = []
        
        # 1. Ngữ cảnh cuộc trò chuyện (chỉ 1 turn gần nhất)
        if conversation_history and len(conversation_history) > 0:
            last_turn = conversation_history[-1]
            if last_turn.get('user'):
                prompt_parts.append(f"Trước đó chủ công hỏi: {last_turn['user'][:150]}...")
            prompt_parts.append("")
        
        # 2. Context từ RAG (tối đa 2 context, ngắn gọn)
        if relevant_contexts:
            prompt_parts.append("Tham khảo:")
            for i, ctx in enumerate(relevant_contexts[:2], 1):  # Chỉ 2 context
                content = ctx.get("content", "")[:200] + "..."  # Giới hạn 200 chars
                metadata = ctx.get("metadata", {})
                
                title = metadata.get("story_title", "")
                if title:
                    prompt_parts.append(f"{i}. {title}: {content}")
                else:
                    prompt_parts.append(f"{i}. {content}")
            prompt_parts.append("")
        
        # 3. Câu hỏi và yêu cầu
        prompt_parts.append(f"Câu hỏi: {user_question}")
        prompt_parts.append("")
        prompt_parts.append(f"Hãy trả lời như {character.name}, gọi người hỏi là 'chủ công', đưa ra lời khuyên thiết thực.")
        
        return "\n".join(prompt_parts)
    
    def build_follow_up_questions(self, character: Character, advice_given: str) -> List[str]:
        """Tạo câu hỏi follow-up phù hợp với nhân vật"""
        persona = self.character_personas.get(character.id, {})
        
        if character.id == "zhuge_liang":
            return [
                "Chủ công có muốn thần giải thích rõ hơn về chiến lược này không?",
                "Chủ công đã cân nhắc các yếu tố rủi ro chưa?",
                "Có điều gì khác chủ công muốn tham khảo thêm không?"
            ]
        elif character.id == "sima_yi":
            return [
                "Chủ công có đủ kiên nhẫn để thực hiện kế hoạch dài hạn này không?",
                "Chủ công có nghĩ đến những biến động có thể xảy ra không?",
                "Còn khía cạnh nào khác chủ công muốn thảo luận?"
            ]
        else:
            return [
                "Chủ công còn thắc mắc gì khác không?",
                "Có điều gì cần làm rõ thêm không?",
                "Chủ công muốn nghe thêm kinh nghiệm nào khác?"
            ]
    
    def validate_response(self, response: str, character: Character) -> Tuple[bool, List[str]]:
        """Kiểm tra chất lượng phản hồi"""
        issues = []
        persona = self.character_personas.get(character.id, {})
        address_style = persona.get("address_style", "chủ công")
        
        # Kiểm tra xưng hô
        if not response.startswith("Thưa chủ công") and "chủ công" not in response[:100]:
            issues.append("Thiếu xưng hô đúng cách")
        
        # Kiểm tra độ dài (điều chỉnh cho max_tokens=400)
        if len(response) < 100:
            issues.append("Phản hồi quá ngắn")
        elif len(response) > 2000:  # Tăng lên 2000 để phù hợp với max_tokens=400
            issues.append("Phản hồi quá dài")
        
        # Kiểm tra nội dung hiện đại (cho phép một số thuật ngữ hiện đại do tư vấn cuộc sống hiện tại)
        inappropriate_terms = ["internet mạng", "smartphone điện thoại", "AI trí tuệ nhân tạo", "**", "###", "markdown"]
        if any(term.lower() in response.lower() for term in inappropriate_terms):
            issues.append("Có sử dụng format hoặc thuật ngữ không phù hợp")
        
        # Kiểm tra tính cách nhân vật (điều chỉnh cho vai trò tư vấn)
        if character.id == "zhuge_liang":
            advisor_keywords = ["chủ công", "thần", "tận tâm", "phân tích", "kế hoạch", "chiến lược"]
            if not any(keyword in response.lower() for keyword in advisor_keywords):
                issues.append("Thiếu thể hiện vai trò quân sư tư vấn của Gia Cát Lượng")
        
        return len(issues) == 0, issues
    
    def enhance_response_with_character_traits(self, response: str, character: Character) -> str:
        """Tăng cường phản hồi với đặc điểm nhân vật"""
        persona = self.character_personas.get(character.id, {})
        
        # Sửa format hiện đại thành format cổ điển
        response = self._fix_modern_formatting(response)
        
        if not persona:
            return response
        
        # Thêm speech patterns nếu chưa có
        speech_patterns = persona.get("speech_patterns", [])
        if speech_patterns and not any(pattern in response for pattern in speech_patterns[:3]):
            # Thêm một speech pattern phù hợp vào đầu câu thứ hai
            lines = response.split('\n')
            if len(lines) > 1:
                lines[1] = f"{speech_patterns[0]}, {lines[1]}" if lines[1] else speech_patterns[0]
                response = '\n'.join(lines)
        
        return response
    
    def _fix_modern_formatting(self, response: str) -> str:
        """Sửa format hiện đại thành format cổ điển"""
        # Loại bỏ markdown bold
        response = re.sub(r'\*\*(.*?)\*\*', r'\1', response)
        
        # Loại bỏ markdown headers
        response = re.sub(r'#+\s*(.*)', r'\1', response)
        
        # Chuyển đổi numbered lists hiện đại
        response = re.sub(r'^(\s*)(\d+)\.\s*', r'\1Thứ \2, ', response, flags=re.MULTILINE)
        
        # Chuyển đổi bullet points
        response = re.sub(r'^(\s*)[-*]\s*', r'\1', response, flags=re.MULTILINE)
        
        return response


# Singleton instance
_qwen_prompt_builder: Optional[QwenPromptBuilder] = None

def get_qwen_prompt_builder() -> QwenPromptBuilder:
    """Get singleton QwenPromptBuilder instance"""
    global _qwen_prompt_builder
    if _qwen_prompt_builder is None:
        _qwen_prompt_builder = QwenPromptBuilder()
    return _qwen_prompt_builder
