# backend/app/api/v1/rag.py

"""
RAG API endpoints
Cung cấp các API để tương tác với hệ thống RAG
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from app.models.characters import (
    Character, CharacterStory, AdviceRequest, AdviceResponse,
    get_character_by_id, get_all_characters
)
from app.core.rag_agent import RAGAgent
from app.core.ai_models import ChatAI, get_chat_ai
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Global RAG agent instance
rag_agent: Optional[RAGAgent] = None


def get_rag_agent() -> RAGAgent:
    """Get RAG agent instance"""
    global rag_agent
    if rag_agent is None:
        rag_agent = RAGAgent()
    return rag_agent


# Request/Response Models
class InitializeKnowledgeBaseRequest(BaseModel):
    character_ids: List[str] = Field(..., description="List of character IDs to initialize")
    force_recreate: bool = Field(False, description="Force recreate knowledge base")


class AddStoryRequest(BaseModel):
    character_id: str = Field(..., description="Character ID")
    stories: List[CharacterStory] = Field(..., description="List of stories to add")


class KnowledgeBaseStatsResponse(BaseModel):
    total_documents: int
    characters: Dict[str, int]
    content_types: Dict[str, int]
    collection_name: str


class SearchContextRequest(BaseModel):
    query: str = Field(..., description="Search query")
    character_id: str = Field(..., description="Character ID to search for")
    top_k: int = Field(5, description="Number of results to return")


class ContextResult(BaseModel):
    content: str
    metadata: Dict[str, Any]
    similarity_score: float
    rank: int


class SearchContextResponse(BaseModel):
    query: str
    character_id: str
    results: List[ContextResult]


# API Endpoints
@router.get("/characters", response_model=Dict[str, Character])
async def list_characters():
    """List all available characters"""
    try:
        characters = get_all_characters()
        return characters
    except Exception as e:
        logger.error(f"Failed to list characters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/characters/{character_id}", response_model=Character)
async def get_character(character_id: str):
    """Get character by ID"""
    try:
        character = get_character_by_id(character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        return character
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get character: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge-base/initialize")
async def initialize_knowledge_base(
    request: InitializeKnowledgeBaseRequest,
    background_tasks: BackgroundTasks
):
    """Initialize knowledge base with character data"""
    try:
        agent = get_rag_agent()
        
        # Clear existing data if force recreate
        if request.force_recreate:
            for char_id in request.character_ids:
                agent.clear_character_data(char_id)
        
        # Add characters to knowledge base
        def add_character_data():
            for char_id in request.character_ids:
                character = get_character_by_id(char_id)
                if character:
                    # Add character knowledge
                    agent.add_character_knowledge(character)
                    
                    # Load and add stories from JSON files
                    try:
                        import json
                        from pathlib import Path
                        
                        stories_file = Path(f"data/training/{char_id}/conversations.json")
                        if stories_file.exists():
                            with open(stories_file, 'r', encoding='utf-8') as f:
                                stories_data = json.load(f)
                            
                            stories = [CharacterStory(**story) for story in stories_data]
                            agent.add_character_stories(char_id, stories)
                            
                    except Exception as e:
                        logger.warning(f"Failed to load stories for {char_id}: {e}")
        
        # Run in background
        background_tasks.add_task(add_character_data)
        
        return {"message": "Knowledge base initialization started", "character_ids": request.character_ids}
        
    except Exception as e:
        logger.error(f"Failed to initialize knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge-base/add-stories")
async def add_stories(request: AddStoryRequest):
    """Add stories to knowledge base"""
    try:
        agent = get_rag_agent()
        agent.add_character_stories(request.character_id, request.stories)
        
        return {
            "message": f"Added {len(request.stories)} stories for character {request.character_id}",
            "character_id": request.character_id,
            "story_count": len(request.stories)
        }
        
    except Exception as e:
        logger.error(f"Failed to add stories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-base/stats", response_model=KnowledgeBaseStatsResponse)
async def get_knowledge_base_stats():
    """Get knowledge base statistics"""
    try:
        agent = get_rag_agent()
        stats = agent.get_collection_stats()
        return KnowledgeBaseStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Failed to get knowledge base stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SearchContextResponse)
async def search_context(request: SearchContextRequest):
    """Search for relevant context"""
    try:
        agent = get_rag_agent()
        results = agent.retrieve_relevant_context(
            query=request.query,
            character_id=request.character_id,
            top_k=request.top_k
        )
        
        context_results = [ContextResult(**result) for result in results]
        
        return SearchContextResponse(
            query=request.query,
            character_id=request.character_id,
            results=context_results
        )
        
    except Exception as e:
        logger.error(f"Failed to search context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/advice", response_model=AdviceResponse)
async def get_advice(
    request: AdviceRequest,
    chat_ai: ChatAI = Depends(get_chat_ai)
):
    """Get advice from a character using RAG"""
    try:
        # Get character
        character = get_character_by_id(request.character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Get RAG agent
        agent = get_rag_agent()
        
        # Get advice
        response = await agent.get_advice(request, character, chat_ai)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get advice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/knowledge-base/character/{character_id}")
async def clear_character_data(character_id: str):
    """Clear all data for a specific character"""
    try:
        agent = get_rag_agent()
        agent.clear_character_data(character_id)
        
        return {"message": f"Cleared data for character {character_id}"}
        
    except Exception as e:
        logger.error(f"Failed to clear character data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        agent = get_rag_agent()
        stats = agent.get_collection_stats()
        
        return {
            "status": "healthy",
            "rag_agent": "initialized",
            "knowledge_base": {
                "total_documents": stats.get("total_documents", 0),
                "characters": len(stats.get("characters", {}))
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
