"""FAISS Vector Store module for RAG system."""
import faiss
import numpy as np
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    """FAISS vector store for semantic search."""
    
    def __init__(self, dimension: int = 1536):
        """
        Initialize vector store.
        
        Args:
            dimension: Embedding dimension
        """
        self.dimension = dimension
        self.index = None
        self.documents = []
    
    def create_index(self):
        """Create FAISS index."""
        self.index = faiss.IndexFlatL2(self.dimension)
        logger.info("FAISS index created")
    
    def add_vectors(self, vectors: np.ndarray, documents: List[str]):
        """
        Add vectors and documents to index.
        
        Args:
            vectors: Numpy array of embeddings
            documents: List of document texts
        """
        if self.index is None:
            self.create_index()
        
        self.index.add(vectors)
        self.documents.extend(documents)
        logger.info(f"Added {len(documents)} documents to index")
    
    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[tuple]:
        """
        Search for similar documents.
        
        Args:
            query_vector: Query embedding
            top_k: Number of results
            
        Returns:
            List of (document, distance) tuples
        """
        if self.index is None:
            return []
        
        distances, indices = self.index.search(query_vector.reshape(1, -1), top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], distances[0][i]))
        
        return results
    
    def save_index(self, path: str):
        """Save index to disk."""
        if self.index is not None:
            faiss.write_index(self.index, path)
            logger.info(f"Index saved to {path}")
    
    def load_index(self, path: str):
        """Load index from disk."""
        self.index = faiss.read_index(path)
        logger.info(f"Index loaded from {path}")
