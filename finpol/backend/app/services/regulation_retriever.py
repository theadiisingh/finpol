"""Regulation Retriever Service - FAISS-based RAG for regulations."""
from typing import List
import logging

from app.rag.vectorstore import VectorStoreManager

logger = logging.getLogger(__name__)


class RegulationRetriever:
    """FAISS-based regulation retrieval service."""
    
    def __init__(self, index_path: str = None):
        """
        Initialize the retriever.
        
        Args:
            index_path: Path to FAISS vectorstore. Defaults to config value.
        """
        self.index_path = index_path
        self._vectorstore_manager = None
    
    def _get_vectorstore_manager(self) -> VectorStoreManager:
        """Get or create vectorstore manager instance."""
        if self._vectorstore_manager is None:
            self._vectorstore_manager = VectorStoreManager(self.index_path)
        return self._vectorstore_manager
    
    def retrieve(self, query: str) -> List[str]:
        """
        Retrieve relevant regulations using similarity search.
        
        Args:
            query: Search query string
            
        Returns:
            List of page content strings from relevant documents
            
        Raises:
            FileNotFoundError: If vectorstore not found
            RuntimeError: If retrieval fails
        """
        try:
            manager = self._get_vectorstore_manager()
            vectorstore = manager.load_vectorstore()
            
            docs = vectorstore.similarity_search(query, k=3)
            
            results = [doc.page_content for doc in docs]
            logger.info(f"Retrieved {len(results)} documents for query: {query}")
            
            return results
            
        except FileNotFoundError as e:
            logger.error(f"Vectorstore not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve regulations: {e}")
            raise RuntimeError(f"Retrieval failed: {e}")
    
    async def initialize(self):
        """Initialize the retriever with regulations."""
        logger.info("Regulation retriever initialized")
    
    async def search_regulations(self, query: str, top_k: int = 3) -> List[dict]:
        """Search regulations by query (legacy method)."""
        results = self.retrieve(query)
        return [{"content": r} for r in results[:top_k]]
    
    async def get_all_regulations(self) -> List[dict]:
        """Get all available regulations (legacy method)."""
        return []
