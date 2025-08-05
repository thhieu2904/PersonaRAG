# backend/scripts/setup_rag_system.py

"""
Script để setup hệ thống RAG
Khởi tạo vector database và load dữ liệu ban đầu
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import List

# Add current directory to Python path
current_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(current_dir))

from app.core.rag_agent import RAGAgent
from app.models.characters import Character, CharacterStory, PREDEFINED_CHARACTERS
from app.utils.logger import get_logger

logger = get_logger(__name__)


def load_character_stories(character_id: str) -> List[CharacterStory]:
    """Load character stories from JSON file"""
    try:
        # Try both character_id and character name for file paths
        possible_paths = [
            current_dir / "data" / "training" / character_id / "conversations.json",
            current_dir / "data" / "training" / "gia_cat_luong" / "conversations.json" if character_id == "zhuge_liang" else None,
            current_dir / "data" / "training" / "tu_ma_y" / "conversations.json" if character_id == "sima_yi" else None,
        ]
        
        stories_file = None
        for path in possible_paths:
            if path and path.exists():
                stories_file = path
                break
        
        if not stories_file.exists():
            logger.warning(f"Stories file not found: {stories_file}")
            return []
        
        with open(stories_file, 'r', encoding='utf-8') as f:
            stories_data = json.load(f)
        
        stories = []
        for story_data in stories_data:
            story = CharacterStory(**story_data)
            stories.append(story)
        
        logger.info(f"Loaded {len(stories)} stories for {character_id}")
        return stories
        
    except Exception as e:
        logger.error(f"Failed to load stories for {character_id}: {e}")
        return []


def setup_rag_system():
    """Setup RAG system with initial data"""
    try:
        logger.info("Setting up RAG system...")
        
        # Initialize RAG agent
        agent = RAGAgent()
        
        # Process each predefined character
        for character_id, character in PREDEFINED_CHARACTERS.items():
            logger.info(f"Processing character: {character.name}")
            
            # Clear existing data (optional)
            agent.clear_character_data(character_id)
            
            # Add character knowledge
            agent.add_character_knowledge(character)
            
            # Load and add stories
            stories = load_character_stories(character_id)
            if stories:
                agent.add_character_stories(character_id, stories)
            
            logger.info(f"Completed setup for {character.name}")
        
        # Get final stats
        stats = agent.get_collection_stats()
        logger.info(f"RAG system setup completed!")
        logger.info(f"Total documents: {stats.get('total_documents', 0)}")
        logger.info(f"Characters: {list(stats.get('characters', {}).keys())}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup RAG system: {e}")
        return False


def test_rag_system():
    """Test RAG system with sample queries"""
    try:
        logger.info("Testing RAG system...")
        
        agent = RAGAgent()
        
        # Test queries
        test_queries = [
            {
                "character_id": "zhuge_liang",
                "query": "Làm thế nào để trở thành một leader giỏi?"
            },
            {
                "character_id": "sima_yi", 
                "query": "Khi nào tôi nên hành động và khi nào nên chờ đợi?"
            }
        ]
        
        for test in test_queries:
            logger.info(f"Testing query for {test['character_id']}: {test['query']}")
            
            results = agent.retrieve_relevant_context(
                query=test['query'],
                character_id=test['character_id'],
                top_k=3
            )
            
            logger.info(f"Found {len(results)} relevant contexts")
            for i, result in enumerate(results, 1):
                logger.info(f"  {i}. Similarity: {result['similarity_score']:.3f}")
                logger.info(f"     Content: {result['content'][:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to test RAG system: {e}")
        return False


def main():
    """Main function"""
    logger.info("Starting RAG system setup...")
    
    # Setup system
    if not setup_rag_system():
        logger.error("RAG system setup failed!")
        return False
    
    # Test system
    if not test_rag_system():
        logger.error("RAG system test failed!")
        return False
    
    logger.info("RAG system setup and test completed successfully!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
