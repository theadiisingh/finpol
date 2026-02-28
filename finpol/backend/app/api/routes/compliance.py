"""Compliance API routes."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
import logging

from app.models.risk_response_model import ComplianceReport
from app.dependencies import get_compliance_generator, get_regulation_retriever
from app.services.compliance_generator import ComplianceGenerator
from app.services.regulation_retriever import RegulationRetriever

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/report/{transaction_id}", response_model=ComplianceReport)
async def generate_compliance_report(
    transaction_id: str,
    risk_score: int = Query(..., description="Risk score from transaction analysis"),
    risk_level: str = Query(..., description="Risk level from transaction analysis"),
    compliance_gen: ComplianceGenerator = Depends(get_compliance_generator)
):
    """Generate compliance report for a transaction."""
    # Create a minimal report without the actual transaction
    # In production, you'd fetch the full transaction from DB
    report = ComplianceReport(
        transaction_id=transaction_id,
        compliance_status="review_required" if risk_level in ["Medium", "High", "Critical"] else "approved",
        regulations_applied=["AML", "KYC"] if risk_level in ["Medium", "High", "Critical"] else [],
        violations=[],
        recommendations=["Manual review required"] if risk_level in ["Medium", "High", "Critical"] else ["Auto-approved"],
        llm_analysis="Compliance review pending due to risk level: " + risk_level,
        timestamp=datetime.now()
    )
    return report


@router.get("/regulations", response_model=List[dict])
async def list_regulations(
    retriever: RegulationRetriever = Depends(get_regulation_retriever)
):
    """List all available regulations."""
    try:
        return await retriever.get_all_regulations()
    except FileNotFoundError:
        # Return sample regulations if vectorstore not available
        return [
            {"id": "aml_001", "title": "Anti-Money Laundering Act", "content": "Financial institutions must report suspicious transactions over $10,000."},
            {"id": "kyc_001", "title": "Know Your Customer", "content": "Customer identity verification required for all accounts."},
            {"id": "fatf_001", "title": "FATF Guidelines", "content": "International standards for combating money laundering and terrorist financing."}
        ]


@router.post("/regulations/search")
async def search_regulations(
    query: str,
    retriever: RegulationRetriever = Depends(get_regulation_retriever)
):
    """Search regulations by query."""
    try:
        results = await retriever.search_regulations(query)
        return results
    except FileNotFoundError:
        # Return sample results if vectorstore not available
        logger.warning(f"Vectorstore not available, returning sample results for query: {query}")
        return [
            {"content": f"Sample regulation related to: {query}. In production, this would come from the FAISS vectorstore."}
        ]


@router.get("/health")
async def compliance_health():
    """Health check for compliance service."""
    return {"status": "operational", "service": "compliance"}
