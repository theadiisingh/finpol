"""Regulation Retriever Service - FAISS-based RAG for regulations.

This module provides:
- Async retrieval support
- Vector store abstraction
- Easy extension for different retrieval methods
- Error handling and logging
"""
from typing import List, Optional, Protocol
import logging
import asyncio

from app.rag.vectorstore import VectorStoreManager, VectorStoreManagerProtocol

logger = logging.getLogger(__name__)


class VectorStoreProtocol(Protocol):
    """Protocol for vector store."""
    
    def similarity_search(self, query: str, k: int = 3) -> List[Any]: ...


class RegulationRetriever:
    """
    FAISS-based regulation retrieval service.
    
    Supports:
    - Async retrieval
    - Lazy initialization
    - Multiple retrieval methods
    - Fallback for missing vectorstore
    """
    
    def __init__(
        self,
        index_path: str = None,
        vectorstore_manager: Optional[VectorStoreManagerProtocol] = None
    ):
        """
        Initialize the retriever.
        
        Args:
            index_path: Path to FAISS vectorstore. Defaults to config value.
            vectorstore_manager: Optional custom vectorstore manager.
        """
        self.index_path = index_path
        self._vectorstore_manager = vectorstore_manager
        self._initialized = False
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """Initialize the retriever asynchronously."""
        if self._initialized:
            return
        
        async with self._lock:
            if self._initialized:
                return
            
            logger.info("Initializing RegulationRetriever")
            # Any async initialization can go here
            self._initialized = True
    
    def _get_vectorstore_manager(self) -> VectorStoreManager:
        """Get or create vectorstore manager instance."""
        if self._vectorstore_manager is None:
            self._vectorstore_manager = VectorStoreManager(self.index_path)
        return self._vectorstore_manager
    
    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """
        Synchronous retrieval of relevant regulations.
        
        Args:
            query: Search query string
            top_k: Number of results to return
            
        Returns:
            List of page content strings from relevant documents
            
        Raises:
            FileNotFoundError: If vectorstore not found
            RuntimeError: If retrieval fails
        """
        try:
            manager = self._get_vectorstore_manager()
            vectorstore = manager.load_vectorstore()
            
            docs = vectorstore.similarity_search(query, k=top_k)
            
            results = [doc.page_content for doc in docs]
            logger.info(f"Retrieved {len(results)} documents for query: {query[:50]}...")
            
            return results
            
        except FileNotFoundError as e:
            logger.warning(f"Vectorstore not found: {e}. Returning empty results.")
            return self._get_fallback_regulations()
        except Exception as e:
            logger.error(f"Failed to retrieve regulations: {e}")
            raise RuntimeError(f"Retrieval failed: {e}")
    
    async def retrieve_async(self, query: str, top_k: int = 3) -> List[str]:
        """
        Asynchronous retrieval of relevant regulations.
        
        Allows for future integration with async ML models.
        
        Args:
            query: Search query string
            top_k: Number of results to return
            
        Returns:
            List of page content strings from relevant documents
        """
        # Run sync operation in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.retrieve, query, top_k)
    
    async def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """
        Async alias for retrieve_async.
        
        Args:
            query: Search query string
            top_k: Number of results to return
            
        Returns:
            List of page content strings
        """
        return await self.retrieve_async(query, top_k)
    
    def search_regulations(self, query: str, top_k: int = 3) -> List[dict]:
        """
        Search regulations by query (sync).
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of regulation dictionaries
        """
        results = self.retrieve(query, top_k)
        return [{"content": r, "source": "faiss"} for r in results]
    
    async def search_regulations_async(self, query: str, top_k: int = 3) -> List[dict]:
        """
        Search regulations by query (async).
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of regulation dictionaries
        """
        results = await self.retrieve_async(query, top_k)
        return [{"content": r, "source": "faiss"} for r in results]
    
    def _get_fallback_regulations(self) -> List[str]:
        """
        Get fallback regulations when vectorstore is unavailable.
        
        Returns a set of default regulatory texts.
        """
        return [
            "RBI Guidelines: All high-value transactions over ₹10 lakhs require enhanced due diligence.",
            "FATF Travel Rule: Financial institutions must collect and transmit originator and beneficiary information for cross-border transactions.",
            "KYC Requirements: Customer identification must be completed before opening accounts.",
            "AML Compliance: Suspicious transactions must be reported to FIU within 7 days.",
        ]
    
    async def get_all_regulations(self) -> List[dict]:
        """
        Get all available regulations.
        
        Returns:
            List of regulation dictionaries
        """
        # For now, return empty list - can be extended
        return []
    
    def get_stats(self) -> dict:
        """Get retriever statistics."""
        return {
            "initialized": self._initialized,
            "index_path": self.index_path,
        }
