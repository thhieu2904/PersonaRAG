# backend/quick_setup.py

"""
Quick setup to test the fix
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.rag_agent import RAGAgent
from app.models.characters import get_character_by_id
import json

def setup_rag():
    """Quick setup RAG system"""
    print("🚀 Quick RAG Setup...")
    
    try:
        # Initialize RAG Agent
        print("1️⃣ Initializing RAG Agent...")
        agent = RAGAgent()
        
        # Get character
        print("2️⃣ Loading character...")
        character = get_character_by_id("zhuge_liang")
        
        # Load stories
        print("3️⃣ Loading stories...")
        with open("data/training/gia_cat_luong/conversations.json", 'r', encoding='utf-8') as f:
            stories_data = json.load(f)
        
        from app.models.characters import CharacterStory
        stories = [CharacterStory(**story_data) for story_data in stories_data]
        
        print(f"   ✅ Loaded {len(stories)} stories")
        
        # Add to RAG
        print("4️⃣ Adding to RAG system...")
        agent.clear_character_data("zhuge_liang")
        agent.add_character_knowledge(character)
        agent.add_character_stories("zhuge_liang", stories)
        
        print("5️⃣ Testing retrieval...")
        results = agent.retrieve_relevant_context(
            query="Làm thế nào để trở thành leader giỏi?",
            character_id="zhuge_liang",
            top_k=2
        )
        
        print(f"   ✅ Retrieved {len(results)} contexts")
        
        print("\n🎉 RAG setup successful!")
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = setup_rag()
    print("✅ Done!" if success else "❌ Failed!")
