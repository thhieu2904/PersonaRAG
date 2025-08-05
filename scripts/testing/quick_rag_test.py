#!/usr/bin/env python3

import sys
from pathlib import Path

current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

try:
    from app.core.rag_agent import RAGAgent
    
    print("Testing RAG Agent...")
    agent = RAGAgent()
    
    stats = agent.get_collection_stats()
    print(f"Total documents: {stats.get('total_documents', 0)}")
    print(f"Characters: {list(stats.get('characters', {}).keys())}")
    
    # Test search
    results = agent.retrieve_relevant_context(
        query="leadership advice",
        character_id="zhuge_liang",
        top_k=2
    )
    
    print(f"Search results: {len(results)} found")
    for i, result in enumerate(results):
        print(f"  {i+1}. Score: {result.get('similarity_score', 0):.3f}")
        
    print("RAG system is working!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
