"""Embeddings module for RAG system."""
from typing import List, Protocol, Any
import numpy as np
import logging

logger = logging.getLogger(__name__)


class EmbeddingsProvider(Protocol):
    """Protocol for embeddings providers."""
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for text."""
        ...
    
    def embed_documents(self, documents: List[str]) -> np.ndarray:
        """Generate embeddings for multiple documents."""
        ...


def get_embeddings_model() -> Any:
    """
    Get embeddings model instance.
    
    Uses OpenAIEmbeddings from LangChain with OPENAI_API_KEY from config.
    Modular structure for easy provider switching in the future.
    
    Returns:
        OpenAIEmbeddings instance
    """
    from langchain_openai import OpenAIEmbeddings
    from app.config import settings
    
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key
    )


class Embeddings:
    """Text embeddings for semantic search."""
    
    def __init__(self, model_name: str = "text-embedding-3-small"):
        """
        Initialize embeddings model.
        
        Args:
            model_name: Name of embedding model
        """
        self.model_name = model_name
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        # Placeholder - in production use OpenAI embeddings
        # For now, return random vector
        dimension = 1536  # OpenAI ada-002 dimension
        return np.random.randn(dimension)
    
    def embed_documents(self, documents: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple documents.
        
        Args:
            documents: List of documents
            
        Returns:
            Numpy array of embeddings
        """
        embeddings = []
        for doc in documents:
            embedding = self.embed_text(doc)
            embeddings.append(embedding)
        
        logger.info(f"Generated embeddings for {len(documents)} documents")
        return np.array(embeddings)
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for query.
        
        Args:
            query: Query text
            
        Returns:
            Query embedding
        """
        return self.embed_text(query)
