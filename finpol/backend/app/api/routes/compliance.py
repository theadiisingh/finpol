"""Compliance API routes."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.risk_response_model import ComplianceReport
from app.dependencies import get_compliance_generator, get_regulation_retriever
from app.services.compliance_generator import ComplianceGenerator
from app.services.regulation_retriever import RegulationRetriever

router = APIRouter()


@router.post("/report/{transaction_id}", response_model=ComplianceReport)
async def generate_compliance_report(
    transaction_id: str,
    compliance_gen: ComplianceGenerator = Depends(get_compliance_generator)
):
    """Generate compliance report for a transaction."""
    report = await compliance_gen.generate_report(transaction_id)
    return report


@router.get("/regulations", response_model=List[dict])
async def list_regulations(
    retriever: RegulationRetriever = Depends(get_regulation_retriever)
):
    """List all available regulations."""
    return await retriever.get_all_regulations()


@router.post("/regulations/search")
async def search_regulations(
    query: str,
    retriever: RegulationRetriever = Depends(get_regulation_retriever)
):
    """Search regulations by query."""
    results = await retriever.search_regulations(query)
    return results
