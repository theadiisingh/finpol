"""FAISS Vector Store module for RAG system."""
import faiss
import numpy as np
from typing import List, Optional, Protocol, Any
import logging
import os

from langchain_community.vectorstores import FAISS

from app.config import settings
from app.rag.embeddings import get_embeddings_model

logger = logging.getLogger(__name__)


class VectorStoreManagerProtocol(Protocol):
    """Protocol for VectorStoreManager."""
    
    def load_vectorstore(self) -> FAISS: ...
    
    def save_vectorstore(self, texts: List[str], metadatas: Optional[List[dict]] = None) -> FAISS: ...


class VectorStoreManager:
    """Manager for FAISS vector store operations."""
    
    def __init__(self, vector_db_path: Optional[str] = None):
        """
        Initialize VectorStoreManager.
        
        Args:
            vector_db_path: Path to vector database. Defaults to config value.
        """
        self.vector_db_path = vector_db_path or settings.vector_db_path
        self._vectorstore: Optional[FAISS] = None
    
    def load_vectorstore(self) -> FAISS:
        """
        Load vectorstore from disk.
        
        Returns:
            FAISS vectorstore instance
            
        Raises:
            FileNotFoundError: If vectorstore path doesn't exist
        """
        if not os.path.exists(self.vector_db_path):
            raise FileNotFoundError(f"Vectorstore not found at {self.vector_db_path}")
        
        embeddings = get_embeddings_model()
        self._vectorstore = FAISS.load_local(
            self.vector_db_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
        logger.info(f"Vectorstore loaded from {self.vector_db_path}")
        return self._vectorstore
    
    def save_vectorstore(self, texts: List[str], metadatas: Optional[List[dict]] = None) -> FAISS:
        """
        Create and save vectorstore to disk.
        
        Args:
            texts: List of text documents to index
            metadatas: Optional list of metadata for each document
            
        Returns:
            FAISS vectorstore instance
        """
        embeddings = get_embeddings_model()
        
        self._vectorstore = FAISS.from_texts(
            texts=texts,
            embedding=embeddings,
            metadatas=metadatas
        )
        
        os.makedirs(self.vector_db_path, exist_ok=True)
        self._vectorstore.save_local(self.vector_db_path)
        logger.info(f"Vectorstore saved to {self.vector_db_path}")
        return self._vectorstore
    
    @property
    def vectorstore(self) -> Optional[FAISS]:
        """Get current vectorstore instance."""
        return self._vectorstore


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
