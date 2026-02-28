"""RAG Ingestion module for document processing."""
import os
import logging
from typing import List
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.rag.embeddings import get_embeddings_model
from app.rag.vectorstore import VectorStoreManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_pdfs(directory: str) -> List:
    """
    Load all PDFs from a directory.
    
    Args:
        directory: Path to directory containing PDFs
        
    Returns:
        List of loaded documents
    """
    documents = []
    
    if not os.path.exists(directory):
        logger.warning(f"Directory does not exist: {directory}")
        return documents
    
    for filename in os.listdir(directory):
        if filename.lower().endswith(".pdf"):
            filepath = os.path.join(directory, filename)
            logger.info(f"Loading PDF: {filename}")
            try:
                loader = PyPDFLoader(filepath)
                docs = loader.load()
                documents.extend(docs)
                logger.info(f"Loaded {len(docs)} pages from {filename}")
            except Exception as e:
                logger.error(f"Failed to load {filename}: {e}")
    
    return documents


def split_documents(documents: List, chunk_size: int = 1000, chunk_overlap: int = 200) -> List:
    """
    Split documents into chunks using RecursiveCharacterTextSplitter.
    
    Args:
        documents: List of documents to split
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of split documents
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    splits = splitter.split_documents(documents)
    logger.info(f"Split {len(documents)} documents into {len(splits)} chunks")
    return splits


def create_embeddings_and_store(splits: List) -> None:
    """
    Create embeddings from document splits and store in FAISS.
    
    Args:
        splits: List of document splits
    """
    texts = [doc.page_content for doc in splits]
    metadatas = [doc.metadata for doc in splits]
    
    manager = VectorStoreManager()
    manager.save_vectorstore(texts, metadatas)
    logger.info("Embeddings created and stored in FAISS")


def ingest() -> None:
    """
    Main ingestion function.
    
    Loads PDFs from regulations directory, splits into chunks,
    creates embeddings, and stores in FAISS.
    """
    logger.info("Starting document ingestion")
    
    # Get the backend directory path
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    regulations_path = os.path.join(backend_dir, "data", "regulations")
    
    logger.info(f"Loading PDFs from: {regulations_path}")
    
    documents = load_pdfs(regulations_path)
    
    if not documents:
        logger.warning("No documents found to ingest. Creating sample regulations.")
        # Create sample regulations for demo purposes
        sample_regulations = [
            "Anti-Money Laundering (AML) Act: Financial institutions must report suspicious transactions over $10,000 to relevant authorities.",
            "Know Your Customer (KYC) Regulation: All financial institutions must verify customer identity before opening accounts.",
            "Bank Secrecy Act (BSA): Requires financial institutions to assist government agencies in detecting and preventing money laundering.",
            "Patriot Act: Enhanced due diligence requirements for international banking relationships.",
            "FATF Recommendations: International standards for combating money laundering and terrorist financing.",
            "Currency Transaction Reporting: Transactions over $10,000 must be reported to FinCEN.",
            "Suspicious Activity Reports: Financial institutions must file SARs for suspicious transactions.",
            "Customer Identification Program: Banks must implement written CIPs to identify customers."
        ]
        
        # Store sample regulations directly
        texts = sample_regulations
        metadatas = [{"source": f"regulation_{i}"} for i in range(len(sample_regulations))]
        
        manager = VectorStoreManager()
        manager.save_vectorstore(texts, metadatas)
        logger.info(f"Created sample vectorstore with {len(sample_regulations)} regulations")
        return
    
    logger.info(f"Loaded {len(documents)} documents")
    
    splits = split_documents(documents)
    create_embeddings_and_store(splits)
    
    logger.info("Ingestion complete")


if __name__ == "__main__":
    ingest()
