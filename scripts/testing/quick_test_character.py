# backend/quick_test_character.py

"""
Quick test cho character chat system
"""

import sys
import logging
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_path))

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_character_response():
    """Test quick character response"""
    print("🧪 Quick Character Response Test")
    
    try:
        from app.core.character_chat_service import get_character_chat_service
        
        chat_service = get_character_chat_service()
        
        # Start conversation
        success, greeting, session_id = chat_service.start_conversation("zhuge_liang")
        
        if not success:
            print(f"❌ Failed to start: {greeting}")
            return False
        
        print(f"✅ Started conversation")
        print(f"Greeting: {greeting[:200]}...")
        
        # Test one question
        question = "Chào Khổng Minh! Tôi cần lời khuyên về lãnh đạo team."
        
        success, response, metadata = chat_service.chat_with_character(
            character_id="zhuge_liang",
            user_message=question,
            session_id=session_id,
            use_rag=False
        )
        
        if success:
            print(f"✅ Response received")
            print(f"Response: {response[:300]}...")
            if metadata:
                print(f"Validation: {'✅ Valid' if metadata.get('response_valid', True) else '❌ Issues'}")
            return True
        else:
            print(f"❌ Response failed: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_character_response()
