"""Transaction API routes."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from app.models.transaction_model import TransactionCreate, TransactionResponse, Transaction
from app.models.risk_response_model import RiskResponse, RiskResult
from app.dependencies import get_risk_engine, get_compliance_generator, get_regulation_retriever
from app.services.risk_engine import RiskEngine
from app.services.compliance_generator import ComplianceGenerator
from app.services.regulation_retriever import RegulationRetriever
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage (use database in production)
transactions_db = {}


@router.post("/analyze", response_model=RiskResponse)
async def analyze_transaction(
    transaction: Transaction,
    risk_engine: RiskEngine = Depends(get_risk_engine),
    compliance_gen: ComplianceGenerator = Depends(get_compliance_generator),
    regulation_retriever: RegulationRetriever = Depends(get_regulation_retriever)
) -> RiskResponse:
    """
    Analyze a transaction for risk and compliance.
    
    Flow:
    1. Accept Transaction model
    2. Call RiskEngine to assess risk
    3. If risk is Medium or High:
        - Retrieve regulations
        - Generate compliance explanation
    4. Return RiskResponse model
    """
    try:
        # Step 1: Assess risk
        risk_result = risk_engine.assess_risk(transaction)
        
        # Determine if compliance check is needed
        requires_compliance = risk_result.risk_level in ["Medium", "High"]
        compliance_explanation: Optional[str] = None
        
        if requires_compliance:
            try:
                # Step 2: Retrieve relevant regulations
                regulations = regulation_retriever.retrieve(
                    f"transaction risk {transaction.country} {transaction.merchant_type}"
                )
                
                # Step 3: Generate compliance explanation
                compliance_explanation = compliance_gen.generate(
                    transaction=transaction,
                    reasons=risk_result.factors,
                    regulations=regulations
                )
            except Exception as e:
                logger.warning(f"Compliance generation failed: {e}")
                compliance_explanation = "Compliance review required but detailed analysis unavailable."
        
        # Build response
        should_approve = risk_result.risk_level in ["Low"]
        requires_review = risk_result.risk_level in ["Medium", "High"]
        
        return RiskResponse(
            transaction_id=transaction.transaction_id,
            risk_score=risk_result.risk_score,
            risk_level=risk_result.risk_level,
            should_approve=should_approve,
            requires_review=requires_review,
            compliance_explanation=compliance_explanation
        )
        
    except Exception as e:
        logger.error(f"Transaction analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    risk_engine: RiskEngine = Depends(get_risk_engine),
    compliance_gen: ComplianceGenerator = Depends(get_compliance_generator)
):
    """Create a new transaction with risk assessment."""
    transaction_id = str(uuid.uuid4())
    
    # Assess risk
    risk_result = risk_engine.assess_risk(transaction)
    
    # Store transaction
    transactions_db[transaction_id] = {
        "id": transaction_id,
        **transaction.model_dump(),
        "risk_score": risk_result.risk_score,
        "risk_level": risk_result.risk_level
    }
    
    return TransactionResponse(
        id=transaction_id,
        **transaction.model_dump(),
        risk_score=risk_result.risk_score,
        risk_level=risk_result.risk_level
    )


@router.get("/", response_model=List[TransactionResponse])
async def list_transactions():
    """List all transactions."""
    return [TransactionResponse(**t) for t in transactions_db.values()]


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str):
    """Get a specific transaction."""
    if transaction_id not in transactions_db:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return TransactionResponse(**transactions_db[transaction_id])
