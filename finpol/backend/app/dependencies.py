"""Application dependencies with proper dependency injection.

This module provides FastAPI dependency injection with:
- Async support
- Proper lifecycle management
- Service abstraction for ML model integration
- Factory pattern for scalability
"""
from typing import Protocol, Generator, Optional, AsyncGenerator
from functools import lru_cache
import logging

from app.config import settings

logger = logging.getLogger(__name__)


# ============================================================
# Protocol Definitions (Interfaces for dependency injection)
# ============================================================


class RiskEngineProtocol(Protocol):
    """Protocol for Risk Engine service."""
    
    def evaluate(self, transaction: "Transaction") -> dict: ...
    def assess_risk(self, transaction: "Transaction") -> "RiskResult": ...


class RegulationRetrieverProtocol(Protocol):
    """Protocol for Regulation Retriever service."""
    
    async def retrieve(self, query: str) -> list[str]: ...
    async def search_regulations(self, query: str, top_k: int = 3) -> list[dict]: ...


class ComplianceGeneratorProtocol(Protocol):
    """Protocol for Compliance Generator service."""
    
    async def generate(
        self,
        transaction: "Transaction",
        reasons: list[str],
        regulations: list[str]
    ) -> str: ...


class VectorStoreManagerProtocol(Protocol):
    """Protocol for Vector Store Manager."""
    
    def load_vectorstore(self) -> any: ...
    def save_vectorstore(self, texts: list[str], metadatas: Optional[list[dict]] = None) -> any: ...


# ============================================================
# Service Factory (for future ML model integration)
# ============================================================


class ServiceFactory:
    """
    Factory for creating service instances.
    
    Supports lazy initialization and singleton pattern.
    Ready for future ML model integration (TensorFlow, PyTorch, etc.)
    """
    
    _instances: dict = {}
    
    @classmethod
    def get_risk_engine(cls) -> "RiskEngineProtocol":
        """Get or create Risk Engine instance."""
        if "risk_engine" not in cls._instances:
            from app.services.risk_engine import RiskEngine
            cls._instances["risk_engine"] = RiskEngine()
            logger.info("RiskEngine instance created")
        return cls._instances["risk_engine"]
    
    @classmethod
    def get_regulation_retriever(cls) -> "RegulationRetrieverProtocol":
        """Get or create Regulation Retriever instance."""
        if "regulation_retriever" not in cls._instances:
            from app.services.regulation_retriever import RegulationRetriever
            cls._instances["regulation_retriever"] = RegulationRetriever(
                index_path=settings.vector_db_path
            )
            logger.info("RegulationRetriever instance created")
        return cls._instances["regulation_retriever"]
    
    @classmethod
    def get_compliance_generator(cls) -> "ComplianceGeneratorProtocol":
        """Get or create Compliance Generator instance."""
        if "compliance_generator" not in cls._instances:
            from app.services.compliance_generator import ComplianceGenerator
            cls._instances["compliance_generator"] = ComplianceGenerator()
            logger.info("ComplianceGenerator instance created")
        return cls._instances["compliance_generator"]
    
    @classmethod
    def get_vectorstore_manager(cls) -> VectorStoreManagerProtocol:
        """Get or create Vector Store Manager instance."""
        if "vectorstore_manager" not in cls._instances:
            from app.rag.vectorstore import VectorStoreManager
            cls._instances["vectorstore_manager"] = VectorStoreManager(
                vector_db_path=settings.vector_db_path
            )
            logger.info("VectorStoreManager instance created")
        return cls._instances["vectorstore_manager"]
    
    @classmethod
    def clear_instances(cls) -> None:
        """Clear all cached instances (useful for testing)."""
        cls._instances.clear()
        logger.info("Service factory instances cleared")


# ============================================================
# FastAPI Dependency Injection Functions
# ============================================================


def get_risk_engine() -> Generator[RiskEngineProtocol, None, None]:
    """
    FastAPI dependency for Risk Engine.
    
    Yields:
        RiskEngine instance
    """
    yield ServiceFactory.get_risk_engine()


def get_regulation_retriever() -> Generator[RegulationRetrieverProtocol, None, None]:
    """
    FastAPI dependency for Regulation Retriever.
    
    Yields:
        RegulationRetriever instance
    """
    yield ServiceFactory.get_regulation_retriever()


def get_compliance_generator() -> Generator[ComplianceGeneratorProtocol, None, None]:
    """
    FastAPI dependency for Compliance Generator.
    
    Yields:
        ComplianceGenerator instance
    """
    yield ServiceFactory.get_compliance_generator()


def get_vectorstore_manager() -> Generator[VectorStoreManagerProtocol, None, None]:
    """
    FastAPI dependency for Vector Store Manager.
    
    Yields:
        VectorStoreManager instance
    """
    yield ServiceFactory.get_vectorstore_manager()


# ============================================================
# Legacy compatibility (deprecated - use above functions)
# ============================================================


@lru_cache
def get_settings() -> settings.__class__:
    """Get settings instance (legacy compatibility)."""
    return settings


# Keep for backward compatibility
risk_engine = ServiceFactory.get_risk_engine
regulation_retriever = ServiceFactory.get_regulation_retriever
compliance_generator = ServiceFactory.get_compliance_generator
