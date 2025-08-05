# backend/simple_test.py

"""
Simple test to check everything works
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test basic imports"""
    print("🧪 Testing imports...")
    
    try:
        from app.models.characters import get_character_by_id, CharacterStory
        print("   ✅ Character models")
        
        from app.core.rag_agent import RAGAgent
        print("   ✅ RAG Agent")
        
        from app.core.prompt_builder import CharacterPromptBuilder
        print("   ✅ Prompt Builder")
        
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False

def test_character_loading():
    """Test character loading"""
    print("\n📚 Testing character loading...")
    
    try:
        from app.models.characters import get_character_by_id
        
        char = get_character_by_id("zhuge_liang")
        print(f"   ✅ Character: {char.name}")
        
        return True
    except Exception as e:
        print(f"   ❌ Character loading failed: {e}")
        return False

def test_story_parsing():
    """Test story parsing with new format"""
    print("\n📖 Testing story parsing...")
    
    try:
        import json
        from app.models.characters import CharacterStory
        
        # Load stories
        with open("data/training/gia_cat_luong/conversations.json", 'r', encoding='utf-8') as f:
            stories_data = json.load(f)
        
        # Parse first story
        story = CharacterStory(**stories_data[0])
        print(f"   ✅ Story: {story.title}")
        print(f"   ✅ Character ID: {story.character_id}")
        print(f"   ✅ Tags: {story.tags}")
        print(f"   ✅ Tags as string: {', '.join(story.tags)}")
        
        return True
    except Exception as e:
        print(f"   ❌ Story parsing failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running Quick Tests")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_character_loading,
        test_story_parsing
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    print("📋 Test Summary:")
    print(f"   Passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! System is ready.")
        print("\n📋 Next steps:")
        print("   1. poetry run python scripts/setup_rag_system.py")
        print("   2. poetry run uvicorn app.main:app --reload")
        print("   3. Open: http://localhost:8000/docs")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
