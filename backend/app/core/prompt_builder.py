# backend/app/core/prompt_builder.py

"""
Prompt Builder cho hệ thống RAG
Xây dựng và quản lý các prompt cho các nhân vật khác nhau
Tích hợp với Advanced Prompt Builder cho Qwen2.5-Instruct
"""

import re
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.models.characters import Character, CharacterType
from .advanced_prompt_builder import get_qwen_prompt_builder


class PromptTemplate:
    """Template for building prompts"""
    
    def __init__(self, template: str, variables: List[str]):
        self.template = template
        self.variables = variables
    
    def format(self, **kwargs) -> str:
        """Format template with provided variables"""
        return self.template.format(**kwargs)
    
    def validate_variables(self, **kwargs) -> bool:
        """Check if all required variables are provided"""
        return all(var in kwargs for var in self.variables)


class CharacterPromptBuilder:
    """Builder for character-specific prompts - Enhanced with Qwen2.5 optimization"""
    
    def __init__(self):
        self.base_templates = self._load_base_templates()
        self.character_specific_templates = self._load_character_templates()
        self.qwen_builder = get_qwen_prompt_builder()  # Advanced builder for Qwen2.5
    
    def build_optimized_prompt(
        self,
        character: Character,
        user_question: str,
        relevant_contexts: List[Dict[str, Any]] = None,
        conversation_history: List[Dict[str, str]] = None,
        style: str = "comprehensive"
    ) -> tuple[str, str]:
        """
        Build optimized prompt for Qwen2.5-Instruct
        Returns: (system_prompt, user_prompt)
        """
        # Sử dụng advanced prompt builder cho Qwen2.5
        system_prompt = self.qwen_builder.build_system_prompt(character)
        user_prompt = self.qwen_builder.build_user_prompt(
            character, 
            user_question, 
            relevant_contexts, 
            conversation_history
        )
        
        return system_prompt, user_prompt
    
    def validate_and_enhance_response(
        self, 
        response: str, 
        character: Character
    ) -> tuple[str, bool, List[str]]:
        """
        Validate và enhance phản hồi
        Returns: (enhanced_response, is_valid, issues)
        """
        is_valid, issues = self.qwen_builder.validate_response(response, character)
        enhanced_response = self.qwen_builder.enhance_response_with_character_traits(response, character)
        
        return enhanced_response, is_valid, issues
    
    def _load_base_templates(self) -> Dict[str, PromptTemplate]:
        """Load base prompt templates"""
        return {
            "greeting": PromptTemplate(
                template="""Tôi là {character_name}, {character_description}. 
Tôi sống vào thời {dynasty}, từ năm {period}.
Tôi sẵn sàng chia sẻ kinh nghiệm và trí tuệ của mình để giúp bạn.""",
                variables=["character_name", "character_description", "dynasty", "period"]
            ),
            
            "advice_intro": PromptTemplate(
                template="""Là {character_name}, tôi hiểu rằng "{user_question}".
Dựa trên kinh nghiệm {expertise} của tôi, tôi có những suy nghĩ sau:""",
                variables=["character_name", "user_question", "expertise"]
            ),
            
            "context_integration": PromptTemplate(
                template="""Từ những tích sử và kinh nghiệm, tôi nhớ đến:
{relevant_contexts}

Điều này gợi cho tôi:""",
                variables=["relevant_contexts"]
            ),
            
            "practical_advice": PromptTemplate(
                template="""Vậy nên, lời khuyên của tôi cho bạn là:

{main_advice}

Hãy nhớ rằng: "{character_wisdom}"

Chúc bạn thành công trên con đường phía trước!""",
                variables=["main_advice", "character_wisdom"]
            )
        }
    
    def _load_character_templates(self) -> Dict[str, Dict[str, PromptTemplate]]:
        """Load character-specific templates"""
        return {
            "zhuge_liang": {
                "opening": PromptTemplate(
                    template="""Như một quân sư từng phụ tá Lưu Bị trong thời loạn lạc, 
tôi luôn tin rằng "tận tâm tận lực, chết mà thôi". 
Với tinh thần này, tôi sẽ tư vấn cho bạn.""",
                    variables=[]
                ),
                "wisdom_style": PromptTemplate(
                    template="""Xưa nay, tôi thường nói: "{quote}". 
Áp dụng vào tình huống của bạn, tôi nghĩ rằng {application}.""",
                    variables=["quote", "application"]
                ),
                "strategic_thinking": PromptTemplate(
                    template="""Trong quân sự, chúng ta có câu "biết người biết ta, trăm trận trăm thắng".
Vậy nên:
1. Hãy phân tích kỹ tình huống: {situation_analysis}
2. Xác định thế mạnh của mình: {strengths}
3. Lên kế hoạch chu đáo: {planning}""",
                    variables=["situation_analysis", "strengths", "planning"]
                )
            },
            
            "sima_yi": {
                "opening": PromptTemplate(
                    template="""Trong suốt cuộc đời, tôi học được rằng kiên nhẫn là vũ khí mạnh nhất.
Không vội vàng, không nóng nảy, mà tính toán kỹ lưỡng mới là con đường đến thành công.""",
                    variables=[]
                ),
                "patience_wisdom": PromptTemplate(
                    template="""Như tôi từng nói: "Thời cơ không đến, tuyệt không hành động".
Trong trường hợp của bạn: {situation_assessment}
Thời điểm thích hợp sẽ là: {timing_advice}""",
                    variables=["situation_assessment", "timing_advice"]
                ),
                "long_term_thinking": PromptTemplate(
                    template="""Tôi luôn nghĩ về lợi ích lâu dài. 
Hành động ngay: {immediate_actions}
Chuẩn bị cho tương lai: {future_preparations}
Kết quả mong đợi: {expected_outcomes}""",
                    variables=["immediate_actions", "future_preparations", "expected_outcomes"]
                )
            }
        }
    
    def build_character_introduction(self, character: Character) -> str:
        """Build character introduction"""
        intro_template = self.base_templates["greeting"]
        
        return intro_template.format(
            character_name=character.name,
            character_description=character.description or f"người {character.character_type.value}",
            dynasty=character.dynasty,
            period=character.period
        )
    
    def build_advice_prompt(
        self,
        character: Character,
        user_question: str,
        relevant_contexts: List[Dict[str, Any]],
        style: str = "comprehensive"
    ) -> str:
        """Build comprehensive advice prompt"""
        
        prompt_parts = []
        
        # 1. Character introduction
        intro = self._build_character_context(character)
        prompt_parts.append(intro)
        
        # 2. User question acknowledgment
        question_intro = self._build_question_context(character, user_question)
        prompt_parts.append(question_intro)
        
        # 3. Relevant contexts if available
        if relevant_contexts:
            context_part = self._build_context_section(relevant_contexts)
            prompt_parts.append(context_part)
        
        # 4. Character-specific opening
        if character.id in self.character_specific_templates:
            opening = self.character_specific_templates[character.id]["opening"]
            prompt_parts.append(opening.format())
        
        # 5. Instructions for response
        instructions = self._build_response_instructions(character, style)
        prompt_parts.append(instructions)
        
        return "\n\n".join(prompt_parts)
    
    def _build_character_context(self, character: Character) -> str:
        """Build character context section"""
        context = f"""Bạn là {character.name} ({character.full_name}), {character.description}.

Thông tin về bạn:
- Triều đại: {character.dynasty}
- Thời kỳ: {character.period}
- Loại nhân vật: {character.character_type.value}
- Xuất thân: {character.origin or 'Không rõ'}

Đặc điểm tính cách chính:
{self._format_list(character.personality_traits)}

Chuyên môn và thế mạnh:
{self._format_list(character.expertise)}

Lĩnh vực kiến thức:
{self._format_list(character.knowledge_domains)}

Phong cách tư vấn: {character.advice_style}
Phong cách nói chuyện: {character.speaking_style}"""

        if character.famous_quotes:
            quote_prefix = '- "'
            quote_suffix = '"'
            context += f"\n\nNhững câu nói nổi tiếng của bạn:\n{self._format_list(character.famous_quotes, prefix=quote_prefix, suffix=quote_suffix)}"
        
        return context
    
    def _build_question_context(self, character: Character, user_question: str) -> str:
        """Build question context section"""
        return f"""Một sinh viên đã hỏi bạn: "{user_question}"

Với tư cách là {character.name}, bạn cần:
- Hiểu sâu vấn đề của sinh viên
- Đưa ra lời khuyên thiết thực
- Sử dụng trí tuệ và kinh nghiệm của mình
- Giữ phong cách nói chuyện đặc trưng"""
    
    def _build_context_section(self, relevant_contexts: List[Dict[str, Any]]) -> str:
        """Build relevant context section"""
        context_text = "Thông tin liên quan từ kinh nghiệm và tích sử:\n\n"
        
        for i, ctx in enumerate(relevant_contexts, 1):
            metadata = ctx.get("metadata", {})
            content = ctx["content"]
            
            # Format context based on type
            if metadata.get("content_type") == "character_profile":
                context_text += f"{i}. Từ hồ sơ cá nhân: {content}\n\n"
            elif metadata.get("story_id"):
                story_title = metadata.get("story_title", "Câu chuyện")
                context_text += f"{i}. {story_title}: {content}\n\n"
            else:
                context_text += f"{i}. {content}\n\n"
        
        return context_text.strip()
    
    def _build_response_instructions(self, character: Character, style: str) -> str:
        """Build response instructions"""
        base_instruction = f"""Hãy trả lời như chính {character.name}, thể hiện:
- Trí tuệ và kinh nghiệm sâu sắc
- Phong cách nói chuyện đặc trưng
- Lời khuyên thiết thực, có thể áp dụng
- Tham khảo kinh nghiệm lịch sử nếu phù hợp"""
        
        if style == "comprehensive":
            base_instruction += f"""

Cấu trúc phản hồi nên bao gồm:
1. Thể hiện sự hiểu biết về vấn đề
2. Chia sẻ kinh nghiệm liên quan (nếu có)
3. Đưa ra lời khuyên cụ thể
4. Kết thúc bằng động viên hoặc câu nói khuyến khích

Lời khuyên của {character.name}:"""
        
        elif style == "concise":
            base_instruction += f"\n\nHãy đưa ra lời khuyên ngắn gọn nhưng súc tích.\n\nLời khuyên của {character.name}:"
        
        return base_instruction
    
    def _format_list(self, items: List[str], prefix: str = "- ", suffix: str = "") -> str:
        """Format a list of items"""
        if not items:
            return "Không có thông tin"
        return "\n".join(f"{prefix}{item}{suffix}" for item in items)
    
    def build_conversation_prompt(
        self,
        character: Character,
        conversation_history: List[Dict[str, str]],
        current_question: str
    ) -> str:
        """Build prompt for continuing a conversation"""
        
        prompt_parts = []
        
        # Character context (shorter for conversations)
        context = f"""Bạn là {character.name}, {character.description}.
Phong cách: {character.speaking_style}"""
        prompt_parts.append(context)
        
        # Conversation history
        if conversation_history:
            history_text = "Cuộc trò chuyện trước đó:\n"
            for turn in conversation_history[-3:]:  # Only last 3 turns
                history_text += f"Sinh viên: {turn.get('user', '')}\n"
                history_text += f"{character.name}: {turn.get('assistant', '')}\n\n"
            prompt_parts.append(history_text)
        
        # Current question
        prompt_parts.append(f"Sinh viên hỏi tiếp: \"{current_question}\"")
        
        # Instructions
        prompt_parts.append(f"Hãy tiếp tục trả lời như {character.name}, giữ tính nhất quán trong cuộc trò chuyện:")
        
        return "\n\n".join(prompt_parts)
    
    def extract_wisdom_quotes(self, character: Character, topic: str = "") -> List[str]:
        """Extract relevant wisdom quotes for a topic"""
        relevant_quotes = []
        
        # Get all quotes
        all_quotes = character.famous_quotes
        
        if not topic:
            return all_quotes
        
        # Simple keyword matching for relevance
        topic_keywords = topic.lower().split()
        
        for quote in all_quotes:
            quote_lower = quote.lower()
            # Check if any topic keyword appears in the quote
            if any(keyword in quote_lower for keyword in topic_keywords):
                relevant_quotes.append(quote)
        
        # If no relevant quotes found, return a few general ones
        if not relevant_quotes and all_quotes:
            relevant_quotes = all_quotes[:2]
        
        return relevant_quotes
    
    def generate_follow_up_questions(self, character: Character, advice_given: str) -> List[str]:
        """Generate follow-up questions that the character might ask"""
        
        follow_ups = []
        
        if character.id == "zhuge_liang":
            follow_ups = [
                "Bạn có muốn tôi giải thích thêm về chiến lược này?",
                "Bạn đã cân nhắc các rủi ro tiềm ẩn chưa?",
                "Có điều gì khác bạn muốn tham khảo không?"
            ]
        elif character.id == "sima_yi":
            follow_ups = [
                "Bạn có đủ kiên nhẫn để thực hiện kế hoạch dài hạn này?",
                "Bạn đã nghĩ đến những thay đổi có thể xảy ra chưa?",
                "Còn khía cạnh nào khác bạn muốn thảo luận?"
            ]
        else:
            follow_ups = [
                "Bạn còn thắc mắc gì khác không?",
                "Có điều gì cần làm rõ thêm?",
                "Bạn muốn nghe thêm kinh nghiệm nào khác?"
            ]
        
        return follow_ups
