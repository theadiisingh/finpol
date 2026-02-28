"""Transaction API routes."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.transaction_model import TransactionCreate, TransactionResponse
from app.models.risk_response_model import RiskResponse
from app.dependencies import get_risk_engine, get_compliance_generator
from app.services.risk_engine import RiskEngine
from app.services.compliance_generator import ComplianceGenerator
import uuid

router = APIRouter()

# In-memory storage (use database in production)
transactions_db = {}


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
