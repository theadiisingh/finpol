"""Regulation Retriever Service - FAISS-based RAG for regulations."""
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class RegulationRetriever:
    """FAISS-based regulation retrieval service."""
    
    def __init__(self, index_path: str = None, data_path: str = None):
        self.index_path = index_path
        self.data_path = data_path
        self.faiss_index = None
        self.regulations = []
    
    async def initialize(self):
        """Initialize the retriever with regulations."""
        # Sample regulations data
        self.regulations = [
            {
                "id": "RBI-AML-001",
                "title": "RBI AML Guidelines",
                "content": "Anti-Money Laundering guidelines per RBI directives",
                "type": "AML"
            },
            {
                "id": "KYC-MD-001",
                "title": "KYC Master Direction",
                "content": "Know Your Customer master direction guidelines",
                "type": "KYC"
            },
            {
                "id": "FATF-001",
                "title": "FATF Guidelines",
                "content": "Financial Action Task Force guidelines",
                "type": "FATF"
            }
        ]
        logger.info("Regulation retriever initialized")
    
    async def search_regulations(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search regulations by query."""
        if not self.regulations:
            await self.initialize()
        
        # Simple keyword-based search (use FAISS in production)
        results = []
        query_lower = query.lower()
        
        for reg in self.regulations:
            if query_lower in reg.get("content", "").lower() or query_lower in reg.get("title", "").lower():
                results.append(reg)
        
        return results[:top_k]
    
    async def get_all_regulations(self) -> List[Dict]:
        """Get all available regulations."""
        if not self.regulations:
            await self.initialize()
        return self.regulations
