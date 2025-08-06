# backend/app/core/rag_agent.py

"""
RAG Agent cho hệ thống tư vấn nhân vật lịch sử
Thực hiện retrieve và generate dựa trên vector database
"""

import asyncio
import logging
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from app.models.characters import Character, CharacterStory, AdviceRequest, AdviceResponse
from app.core.ai_models import ChatAI
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentChunk:
    """Represent a chunk of document with metadata"""
    
    def __init__(self, content: str, metadata: Dict[str, Any]):
        self.content = content
        self.metadata = metadata
        self.embedding: Optional[np.ndarray] = None


class RAGAgent:
    """RAG Agent for historical character advice system"""
    
    def __init__(
        self,
        model_name: str = "keepitreal/vietnamese-sbert",
        chroma_db_path: str = "./data/chroma_db",
        collection_name: str = "character_knowledge"
    ):
        self.model_name = model_name
        self.chroma_db_path = Path(chroma_db_path)
        self.collection_name = collection_name
        
        # Initialize components
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self.chat_ai = None
        
        # Configuration
        self.chunk_size = 512
        self.chunk_overlap = 50
        self.top_k_results = 5
        
        self._initialize()
    
    def _initialize(self):
        """Initialize all components"""
        try:
            logger.info("Initializing RAG Agent...")
            
            # Initialize embedding model
            logger.info(f"Loading embedding model: {self.model_name}")
            self.embedding_model = SentenceTransformer(self.model_name)
            
            # Initialize Chroma DB
            logger.info("Initializing Chroma DB...")
            self.chroma_db_path.mkdir(parents=True, exist_ok=True)
            
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.chroma_db_path),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            try:
                self.collection = self.chroma_client.get_collection(
                    name=self.collection_name
                )
                logger.info(f"Loaded existing collection: {self.collection_name}")
            except Exception:
                # Create new collection
                self.collection = self.chroma_client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Historical character knowledge base"}
                )
                logger.info(f"Created new collection: {self.collection_name}")
            
            logger.info("RAG Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG Agent: {e}")
            raise
    
    def _chunk_text(self, text: str, character_id: str, source: str = "") -> List[DocumentChunk]:
        """Split text into chunks for processing"""
        chunks = []
        
        # Simple chunking by sentences for now
        sentences = text.split('. ')
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk.strip():
                    chunks.append(DocumentChunk(
                        content=current_chunk.strip(),
                        metadata={
                            "character_id": character_id,
                            "source": source,
                            "chunk_length": len(current_chunk)
                        }
                    ))
                current_chunk = sentence + ". "
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(DocumentChunk(
                content=current_chunk.strip(),
                metadata={
                    "character_id": character_id,
                    "source": source,
                    "chunk_length": len(current_chunk)
                }
            ))
        
        return chunks
    
    def add_character_stories(self, character_id: str, stories: List[CharacterStory]):
        """Add character stories to the knowledge base"""
        try:
            logger.info(f"Adding {len(stories)} stories for character {character_id}")
            
            all_chunks = []
            for story in stories:
                # Chunk the story content
                chunks = self._chunk_text(
                    text=f"Tiêu đề: {story.title}\n\nNội dung: {story.content}",
                    character_id=character_id,
                    source=f"story_{story.id}"
                )
                
                # Add story metadata to chunks
                for chunk in chunks:
                    chunk.metadata.update({
                        "story_id": story.id,
                        "story_title": story.title,
                        "category": story.category,
                        "tags": ", ".join(story.tags) if story.tags else "",
                        "lesson": story.lesson or "",
                        "relevance_score": story.relevance_score
                    })
                
                all_chunks.extend(chunks)
            
            # Generate embeddings
            contents = [chunk.content for chunk in all_chunks]
            embeddings = self.embedding_model.encode(contents).tolist()
            
            # Prepare data for Chroma
            ids = [f"{character_id}_story_{i}" for i in range(len(all_chunks))]
            metadatas = [chunk.metadata for chunk in all_chunks]
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Successfully added {len(all_chunks)} chunks to knowledge base")
            
        except Exception as e:
            logger.error(f"Failed to add character stories: {e}")
            raise
    
    def add_character_knowledge(self, character: Character):
        """Add general character knowledge to the database"""
        try:
            logger.info(f"Adding knowledge for character: {character.name}")
            
            # Create knowledge text from character info
            knowledge_text = f"""
            Tên: {character.name} ({character.full_name})
            Triều đại: {character.dynasty}
            Thời kỳ: {character.period}
            Xuất thân: {character.origin or 'Không rõ'}
            
            Đặc điểm tính cách: {', '.join(character.personality_traits)}
            Chuyên môn: {', '.join(character.expertise)}
            Lĩnh vực kiến thức: {', '.join(character.knowledge_domains)}
            
            Phong cách tư vấn: {character.advice_style}
            Phong cách nói chuyện: {character.speaking_style}
            
            Câu nói nổi tiếng:
            {chr(10).join(f'- {quote}' for quote in character.famous_quotes)}
            
            Mô tả: {character.description or ''}
            """
            
            chunks = self._chunk_text(
                text=knowledge_text,
                character_id=character.id,
                source="character_profile"
            )
            
            # Add character metadata to chunks
            for chunk in chunks:
                chunk.metadata.update({
                    "content_type": "character_profile",
                    "character_name": character.name,
                    "dynasty": character.dynasty,
                    "character_type": character.character_type.value
                })
            
            # Generate embeddings and add to collection
            contents = [chunk.content for chunk in chunks]
            embeddings = self.embedding_model.encode(contents).tolist()
            
            ids = [f"{character.id}_profile_{i}" for i in range(len(chunks))]
            metadatas = [chunk.metadata for chunk in chunks]
            
            self.collection.add(
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Successfully added character knowledge for {character.name}")
            
        except Exception as e:
            logger.error(f"Failed to add character knowledge: {e}")
            raise
    
    def retrieve_relevant_context(
        self, 
        query: str, 
        character_id: str, 
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant context for a query"""
        try:
            if top_k is None:
                top_k = self.top_k_results
            
            logger.info(f"Retrieving context for query: {query[:100]}...")
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Search in collection with character filter
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"character_id": character_id}
            )
            
            # Format results
            contexts = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0], 
                    results['distances'][0]
                )):
                    contexts.append({
                        "content": doc,
                        "metadata": metadata,
                        "similarity_score": 1 - distance,  # Convert distance to similarity
                        "rank": i + 1
                    })
            
            logger.info(f"Retrieved {len(contexts)} relevant contexts")
            return contexts
            
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            return []
    
    def generate_character_prompt(
        self, 
        character: Character, 
        user_question: str,
        relevant_contexts: List[Dict[str, Any]]
    ) -> str:
        """Generate prompt for the character-based response"""
        
        # ⚠️ DEPRECATED: Chuyển sang sử dụng QwenPromptBuilder để đảm bảo xưng hô nhất quán
        from app.core.advanced_prompt_builder import get_qwen_prompt_builder
        
        prompt_builder = get_qwen_prompt_builder()
        
        # Sử dụng advanced prompt builder với validation nghiêm ngặt
        system_prompt = prompt_builder.build_system_prompt(character)
        user_prompt = prompt_builder.build_user_prompt(
            character,
            user_question,
            relevant_contexts,
            conversation_history=None
        )
        
        # Kết hợp system và user prompt cho RAG endpoint
        combined_prompt = f"""{system_prompt}

{user_prompt}"""
        
        return combined_prompt
    
    async def get_advice(
        self, 
        request: AdviceRequest, 
        character: Character,
        chat_ai: ChatAI
    ) -> AdviceResponse:
        """Get advice from a character based on user request"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            logger.info(f"Getting advice from {character.name} for: {request.user_question[:100]}...")
            
            # Retrieve relevant context
            relevant_contexts = self.retrieve_relevant_context(
                query=request.user_question,
                character_id=character.id,
                top_k=self.top_k_results
            )
            
            # Generate prompt với advanced builder
            prompt = self.generate_character_prompt(
                character=character,
                user_question=request.user_question,
                relevant_contexts=relevant_contexts
            )
            
            # Get response from AI
            advice = chat_ai.chat(prompt)
            
            # ✅ THÊM VALIDATION như trong character_chat_service
            from app.core.advanced_prompt_builder import get_qwen_prompt_builder
            prompt_builder = get_qwen_prompt_builder()
            
            is_valid, issues = prompt_builder.validate_response(advice, character)
            enhanced_advice = prompt_builder.enhance_response_with_character_traits(advice, character)
            
            if not is_valid:
                logger.warning(f"RAG response validation issues: {issues}")
            
            # Calculate response time
            response_time = asyncio.get_event_loop().time() - start_time
            
            # Extract story IDs from contexts
            relevant_story_ids = []
            sources_used = []
            for ctx in relevant_contexts:
                if "story_id" in ctx["metadata"]:
                    relevant_story_ids.append(ctx["metadata"]["story_id"])
                sources_used.append(ctx["metadata"].get("source", "unknown"))
            
            # Calculate confidence score based on context relevance
            confidence_score = 0.8  # Base confidence
            if relevant_contexts:
                avg_similarity = sum(ctx["similarity_score"] for ctx in relevant_contexts) / len(relevant_contexts)
                confidence_score = min(0.95, max(0.5, avg_similarity))
            
            response = AdviceResponse(
                character_id=character.id,
                character_name=character.name,
                advice=enhanced_advice,  # Sử dụng enhanced response
                relevant_stories=relevant_story_ids,
                confidence_score=confidence_score,
                sources_used=sources_used,
                response_time=response_time
            )
            
            logger.info(f"Generated advice from {character.name} in {response_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get advice: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        try:
            count = self.collection.count()
            
            # Get sample of data to analyze
            sample = self.collection.get(limit=min(100, count))
            
            character_counts = {}
            content_types = {}
            
            if sample['metadatas']:
                for metadata in sample['metadatas']:
                    char_id = metadata.get('character_id', 'unknown')
                    content_type = metadata.get('content_type', 'unknown')
                    
                    character_counts[char_id] = character_counts.get(char_id, 0) + 1
                    content_types[content_type] = content_types.get(content_type, 0) + 1
            
            return {
                "total_documents": count,
                "characters": character_counts,
                "content_types": content_types,
                "collection_name": self.collection_name
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}
    
    def clear_character_data(self, character_id: str):
        """Clear all data for a specific character"""
        try:
            logger.info(f"Clearing data for character: {character_id}")
            
            # Get all documents for this character
            results = self.collection.get(
                where={"character_id": character_id}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} documents for {character_id}")
            else:
                logger.info(f"No documents found for character {character_id}")
                
        except Exception as e:
            logger.error(f"Failed to clear character data: {e}")
            raise
