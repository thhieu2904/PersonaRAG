# backend/app/core/character_chat_service.py

"""
Character Chat Service - Service tích hợp cho chat với nhân vật
Sử dụng Advanced Prompt Builder và AI Models được tối ưu
"""

import logging
from typing import Optional, Dict, Any, List, Tuple
import asyncio
from datetime import datetime

from app.models.characters import Character, get_character_by_id
from app.core.ai_models import get_chat_ai, ModelConfig
from app.core.advanced_prompt_builder import get_qwen_prompt_builder
from app.core.rag_agent import RAGAgent

logger = logging.getLogger(__name__)


class CharacterChatService:
    """Service quản lý chat với nhân vật lịch sử"""
    
    def __init__(self, rag_agent: Optional[RAGAgent] = None):
        self.chat_ai = get_chat_ai()
        self.prompt_builder = get_qwen_prompt_builder()  # Sử dụng trực tiếp QwenPromptBuilder
        self.rag_agent = rag_agent
        self.conversation_sessions: Dict[str, List[Dict[str, Any]]] = {}
        
        # Đảm bảo model được load
        if not self.chat_ai.is_loaded:
            logger.info("Loading AI model for character chat...")
            self.chat_ai.load_model()
    
    def start_conversation(
        self, 
        character_id: str, 
        session_id: str = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Bắt đầu cuộc trò chuyện với nhân vật
        Returns: (success, response, session_id)
        """
        character = get_character_by_id(character_id)
        if not character:
            return False, f"Không tìm thấy nhân vật: {character_id}", None
        
        if not session_id:
            session_id = f"{character_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Khởi tạo session mới
        self.conversation_sessions[session_id] = []
        
        # Tạo lời chào đầu tiên
        greeting_response = self._generate_greeting(character)
        
        # Lưu lại trong session
        self.conversation_sessions[session_id].append({
            "type": "greeting",
            "character": character_id,
            "assistant": greeting_response,
            "timestamp": datetime.now().isoformat()
        })
        
        return True, greeting_response, session_id
    
    def chat_with_character(
        self,
        character_id: str,
        user_message: str,
        session_id: str,
        use_rag: bool = True
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Chat với nhân vật
        Returns: (success, response, metadata)
        """
        character = get_character_by_id(character_id)
        if not character:
            return False, f"Không tìm thấy nhân vật: {character_id}", None
        
        if session_id not in self.conversation_sessions:
            return False, "Session không tồn tại. Vui lòng bắt đầu cuộc trò chuyện mới.", None
        
        try:
            # 1. Lấy context từ RAG nếu được yêu cầu
            relevant_contexts = []
            if use_rag and self.rag_agent:
                try:
                    # Sử dụng RAGAgent để search context 
                    search_results = self.rag_agent.retrieve_relevant_context(
                        query=user_message,
                        character_id=character_id,
                        top_k=3
                    )
                    relevant_contexts = search_results
                    logger.info(f"Found {len(relevant_contexts)} relevant contexts from RAG")
                except Exception as e:
                    logger.warning(f"RAG search failed: {e}, continuing without context")
            
            # 2. Lấy lịch sử cuộc trò chuyện
            conversation_history = self._get_conversation_history(session_id)
            
            # 3. Xây dựng prompt với advanced builder
            system_prompt = self.prompt_builder.build_system_prompt(character)
            user_prompt = self.prompt_builder.build_user_prompt(
                character,
                user_message,
                relevant_contexts,
                conversation_history
            )
            
            logger.info(f"Generated prompts - System: {len(system_prompt)} chars, User: {len(user_prompt)} chars")
            
            # 4. Gọi AI model
            response = self.chat_ai.chat(
                user_message=user_prompt,
                system_prompt=system_prompt,
                reset_history=False  # Giữ context trong session
            )
            
            # 5. Validate và enhance response
            is_valid, issues = self.prompt_builder.validate_response(response, character)
            enhanced_response = self.prompt_builder.enhance_response_with_character_traits(response, character)
            
            if not is_valid:
                logger.warning(f"Response validation issues: {issues}")
            
            # 6. Lưu vào session
            self.conversation_sessions[session_id].append({
                "user": user_message,
                "assistant": enhanced_response,
                "contexts_used": len(relevant_contexts),
                "validation_issues": issues if not is_valid else [],
                "timestamp": datetime.now().isoformat()
            })
            
            # 7. Tạo metadata
            metadata = {
                "character_id": character_id,
                "session_id": session_id,
                "contexts_used": len(relevant_contexts),
                "conversation_length": len(self.conversation_sessions[session_id]),
                "response_valid": is_valid,
                "follow_up_questions": self.prompt_builder.build_follow_up_questions(character, enhanced_response)
            }
            
            return True, enhanced_response, metadata
            
        except Exception as e:
            logger.error(f"Chat with character failed: {e}")
            return False, f"Lỗi khi trò chuyện với {character.name}: {str(e)}", None
    
    def _generate_greeting(self, character: Character) -> str:
        """Tạo lời chào đầu tiên từ nhân vật"""
        system_prompt = self.prompt_builder.build_system_prompt(character)
        greeting_prompt = f"""Hãy tự giới thiệu bản thân như {character.name} và chào đón chủ công. 
Giới thiệu ngắn gọn về bản thân và sẵn sàng tư vấn."""
        
        try:
            response = self.chat_ai.chat(
                user_message=greeting_prompt,
                system_prompt=system_prompt,
                reset_history=True
            )
            return self.prompt_builder.enhance_response_with_character_traits(response, character)
        except Exception as e:
            logger.error(f"Failed to generate greeting: {e}")
            return f"Thưa chủ công, tôi là {character.name}. Tôi sẵn sàng tư vấn cho chủ công."
    
    def _get_conversation_history(self, session_id: str, max_turns: int = 3) -> List[Dict[str, str]]:
        """Lấy lịch sử cuộc trò chuyện gần nhất"""
        if session_id not in self.conversation_sessions:
            return []
        
        history = []
        session_data = self.conversation_sessions[session_id]
        
        # Lấy các turn cuối (bỏ qua greeting)
        for item in session_data[-max_turns:]:
            if item.get("type") != "greeting" and "user" in item:
                history.append({
                    "user": item["user"],
                    "assistant": item["assistant"]
                })
        
        return history
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin session"""
        if session_id not in self.conversation_sessions:
            return None
        
        session_data = self.conversation_sessions[session_id]
        
        return {
            "session_id": session_id,
            "total_messages": len(session_data),
            "character_id": session_data[0].get("character") if session_data else None,
            "created_at": session_data[0].get("timestamp") if session_data else None,
            "last_activity": session_data[-1].get("timestamp") if session_data else None
        }
    
    def clear_session(self, session_id: str) -> bool:
        """Xóa session"""
        if session_id in self.conversation_sessions:
            del self.conversation_sessions[session_id]
            # Reset AI chat history
            self.chat_ai.clear_history()
            return True
        return False
    
    def get_available_characters(self) -> List[Dict[str, Any]]:
        """Lấy danh sách nhân vật có sẵn"""
        from app.models.characters import get_all_characters
        
        characters = get_all_characters()
        result = []
        
        for char_id, character in characters.items():
            result.append({
                "id": character.id,
                "name": character.name,
                "full_name": character.full_name,
                "dynasty": character.dynasty,
                "description": character.description,
                "character_type": character.character_type.value,
                "expertise": character.expertise,
                "has_advanced_prompt": char_id in self.prompt_builder.character_personas
            })
        
        return result
    
    def get_model_status(self) -> Dict[str, Any]:
        """Lấy trạng thái model"""
        return {
            "ai_model": self.chat_ai.get_model_info(),
            "active_sessions": len(self.conversation_sessions),
            "rag_available": self.rag_agent is not None
        }


# Singleton instance
_character_chat_service: Optional[CharacterChatService] = None

def get_character_chat_service(rag_agent: Optional[RAGAgent] = None) -> CharacterChatService:
    """Get singleton CharacterChatService instance"""
    global _character_chat_service
    if _character_chat_service is None:
        _character_chat_service = CharacterChatService(rag_agent)
    return _character_chat_service
