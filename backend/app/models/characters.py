# backend/app/models/characters.py

"""
Character models cho hệ thống RAG
Định nghĩa các nhân vật lịch sử và thông tin của họ
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class CharacterType(str, Enum):
    """Enum cho các loại nhân vật"""
    STRATEGIST = "strategist"  # Quân sư
    GENERAL = "general"       # Tướng quân  
    EMPEROR = "emperor"       # Hoàng đế
    SCHOLAR = "scholar"       # Học giả
    ADVISOR = "advisor"       # Cố vấn


class Character(BaseModel):
    """Model cho nhân vật lịch sử"""
    id: str = Field(..., description="ID duy nhất của nhân vật")
    name: str = Field(..., description="Tên nhân vật")
    full_name: Optional[str] = Field(None, description="Tên đầy đủ")
    dynasty: str = Field(..., description="Triều đại")
    period: str = Field(..., description="Thời kỳ (VD: 181-234)")
    character_type: CharacterType = Field(..., description="Loại nhân vật")
    
    # Thông tin cơ bản
    birth_year: Optional[int] = Field(None, description="Năm sinh")
    death_year: Optional[int] = Field(None, description="Năm mất")
    origin: Optional[str] = Field(None, description="Quê quán")
    
    # Đặc điểm tính cách
    personality_traits: List[str] = Field(default_factory=list, description="Đặc điểm tính cách")
    expertise: List[str] = Field(default_factory=list, description="Chuyên môn, thế mạnh")
    famous_quotes: List[str] = Field(default_factory=list, description="Câu nói nổi tiếng")
    
    # Thông tin cho RAG
    knowledge_domains: List[str] = Field(default_factory=list, description="Lĩnh vực kiến thức")
    advice_style: str = Field(..., description="Phong cách tư vấn")
    speaking_style: str = Field(..., description="Phong cách nói chuyện")
    
    # Metadata
    description: Optional[str] = Field(None, description="Mô tả ngắn gọn")
    avatar_url: Optional[str] = Field(None, description="URL ảnh đại diện")
    is_active: bool = Field(True, description="Có hoạt động không")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CharacterStory(BaseModel):
    """Model cho câu chuyện/tích sử của nhân vật"""
    id: str = Field(..., description="ID câu chuyện")
    character_id: str = Field(..., description="ID nhân vật")
    title: str = Field(..., description="Tiêu đề câu chuyện")
    content: str = Field(..., description="Nội dung câu chuyện")
    
    # Phân loại
    category: str = Field(..., description="Danh mục (VD: military, politics, wisdom)")
    tags: List[str] = Field(default_factory=list, description="Tags cho search")
    
    # Metadata cho RAG
    lesson: Optional[str] = Field(None, description="Bài học rút ra")
    relevance_score: float = Field(1.0, description="Điểm liên quan (0-1)")
    target_audience: List[str] = Field(default_factory=list, description="Đối tượng phù hợp")
    
    # Thông tin bổ sung
    source: Optional[str] = Field(None, description="Nguồn tham khảo")
    verified: bool = Field(False, description="Đã xác minh chưa")
    created_at: datetime = Field(default_factory=datetime.now)


class AdviceRequest(BaseModel):
    """Model cho yêu cầu tư vấn"""
    user_question: str = Field(..., description="Câu hỏi của user")
    character_id: str = Field(..., description="ID nhân vật được chọn")
    context: Optional[str] = Field(None, description="Context bổ sung")
    
    # Thông tin user (optional)
    user_role: Optional[str] = Field(None, description="Vai trò của user (student, professional, etc.)")
    difficulty_level: Optional[str] = Field("intermediate", description="Mức độ (beginner, intermediate, advanced)")


class AdviceResponse(BaseModel):
    """Model cho phản hồi tư vấn"""
    character_id: str = Field(..., description="ID nhân vật")
    character_name: str = Field(..., description="Tên nhân vật")
    advice: str = Field(..., description="Lời khuyên")
    
    # Thông tin bổ sung
    relevant_stories: List[str] = Field(default_factory=list, description="ID các câu chuyện liên quan")
    confidence_score: float = Field(1.0, description="Điểm tin cậy (0-1)")
    sources_used: List[str] = Field(default_factory=list, description="Nguồn được sử dụng")
    
    # Metadata
    response_time: float = Field(..., description="Thời gian phản hồi (giây)")
    created_at: datetime = Field(default_factory=datetime.now)


# Predefined characters
PREDEFINED_CHARACTERS = {
    "zhuge_liang": Character(
        id="zhuge_liang",
        name="Gia Cát Lượng",
        full_name="Khổng Minh Gia Cát Lượng",
        dynasty="Tam Quốc",
        period="181-234",
        character_type=CharacterType.STRATEGIST,
        birth_year=181,
        death_year=234,
        origin="Dương Đô, Lưu Dương",
        personality_traits=[
            "Thông minh vượt trội", 
            "Trung thành", 
            "Khiêm tốn", 
            "Có tầm nhìn xa",
            "Tận tâm với nghĩa vụ"
        ],
        expertise=[
            "Quân sự học", 
            "Chính trị học", 
            "Kinh tế học", 
            "Thiên văn học",
            "Phong thủy địa lý"
        ],
        famous_quotes=[
            "Tận tâm tận lực, chết mà sau thôi",
            "Không có việc gì nhỏ, chỉ có việc được làm tốt hay không",
            "Biết người biết ta, trăm trận trăm thắng"
        ],
        knowledge_domains=[
            "Strategy & Planning",
            "Leadership",
            "Team Management", 
            "Problem Solving",
            "Innovation",
            "Diplomacy"
        ],
        advice_style="Sâu sắc, thực tế, có dẫn chứng lịch sử cụ thể",
        speaking_style="Lịch thiệp, khiêm tốn nhưng đầy tự tin, thường dùng ví dụ từ thiên nhiên",
        description="Quân sư tài ba nhất thời Tam Quốc, nổi tiếng với trí tuệ và lòng trung thành"
    ),
    
    "sima_yi": Character(
        id="sima_yi",
        name="Tư Mã Ý",
        full_name="Tư Mã Trọng Đạt",
        dynasty="Tam Quốc - Tây Tấn",
        period="179-251",
        character_type=CharacterType.STRATEGIST,
        birth_year=179,
        death_year=251,
        origin="Ôn Huyện, Hà Nội",
        personality_traits=[
            "Thâm trầm", 
            "Kiên nhẫn", 
            "Tầm nhìn dài hạn", 
            "Khôn ngoan",
            "Có tham vọng lớn"
        ],
        expertise=[
            "Chiến lược dài hạn", 
            "Chính trị nội bộ", 
            "Quản lý nhân sự", 
            "Kinh tế nhà nước",
            "Xây dựng thể chế"
        ],
        famous_quotes=[
            "Kiên nhẫn là vũ khí mạnh nhất của kẻ thông thái",
            "Thời cơ không đến, tuyệt không hành động", 
            "Chiến thắng đích thực là không cần chiến đấu"
        ],
        knowledge_domains=[
            "Long-term Planning",
            "Risk Management", 
            "Organizational Development",
            "Strategic Patience",
            "Change Management",
            "Power Dynamics"
        ],
        advice_style="Thận trọng, phân tích kỹ lưỡng, tập trung vào lợi ích dài hạn",
        speaking_style="Chững chạc, ít nói nhưng khi nói ra là có tính toán kỹ càng",
        description="Quân sư thâm trầm, người sáng lập triều đại Tây Tấn, nổi tiếng với trí tuệ và kiên nhẫn"
    )
}


def get_character_by_id(character_id: str) -> Optional[Character]:
    """Lấy thông tin nhân vật theo ID"""
    return PREDEFINED_CHARACTERS.get(character_id)


def get_all_characters() -> Dict[str, Character]:
    """Lấy tất cả nhân vật"""
    return PREDEFINED_CHARACTERS


def get_characters_by_type(character_type: CharacterType) -> List[Character]:
    """Lấy nhân vật theo loại"""
    return [char for char in PREDEFINED_CHARACTERS.values() if char.character_type == character_type]
