"""Application dependencies."""
from app.services.risk_engine import RiskEngine
from app.services.compliance_generator import ComplianceGenerator
from app.services.regulation_retriever import RegulationRetriever

# Global service instances
risk_engine = RiskEngine()
regulation_retriever = RegulationRetriever()
compliance_generator = ComplianceGenerator(regulation_retriever)


def get_risk_engine() -> RiskEngine:
    """Get risk engine instance."""
    return risk_engine


def get_compliance_generator() -> ComplianceGenerator:
    """Get compliance generator instance."""
    return compliance_generator


def get_regulation_retriever() -> RegulationRetriever:
    """Get regulation retriever instance."""
    return regulation_retriever
