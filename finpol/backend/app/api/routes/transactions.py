"""Transaction API routes with async support and dependency injection.

This module provides:
- Async route handlers
- Proper dependency injection
- Error handling
- Clean service abstraction
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from uuid import uuid4
import logging

from app.models.transaction_model import Transaction, TransactionCreate, TransactionResponse
from app.models.risk_response_model import RiskResponse
from app.dependencies import (
    get_risk_engine,
    get_compliance_generator,
    get_regulation_retriever,
    RiskEngineProtocol,
    RegulationRetrieverProtocol,
    ComplianceGeneratorProtocol
)

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage (use database in production)
transactions_db: dict = {}


@router.post("/analyze", response_model=RiskResponse)
async def analyze_transaction(
    transaction: Transaction,
    risk_engine: RiskEngineProtocol = Depends(get_risk_engine),
    compliance_gen: ComplianceGeneratorProtocol = Depends(get_compliance_generator),
    regulation_retriever: RegulationRetrieverProtocol = Depends(get_regulation_retriever)
) -> RiskResponse:
    """
    Analyze a transaction for risk and compliance.
    
    Flow:
    1. Accept Transaction model
    2. Call RiskEngine to assess risk (async)
    3. If risk is Medium or High:
        - Retrieve regulations (async)
        - Generate compliance explanation (async)
    4. Return RiskResponse model
    
    Args:
        transaction: Transaction to analyze
        risk_engine: Injected risk engine
        compliance_gen: Injected compliance generator
        regulation_retriever: Injected regulation retriever
        
    Returns:
        RiskResponse with risk assessment and compliance explanation
    """
    try:
        transaction_id = getattr(transaction, 'transaction_id', None) or str(uuid4())
        transaction.transaction_id = transaction_id
        
        # Step 1: Assess risk (async for future ML integration)
        risk_result = await risk_engine.assess_risk_async(transaction)
        
        # Determine if compliance check is needed
        requires_compliance = risk_result.risk_level in ["Medium", "High", "Critical"]
        compliance_explanation: Optional[str] = None
        
        if requires_compliance:
            try:
                # Step 2: Retrieve relevant regulations (async)
                query = f"transaction risk {transaction.country} {transaction.merchant_type}"
                regulations = await regulation_retriever.retrieve_async(query)
                
                # Step 3: Generate compliance explanation (async)
                compliance_explanation = await compliance_gen.generate_async(
                    transaction=transaction,
                    reasons=risk_result.factors,
                    regulations=regulations
                )
            except Exception as e:
                logger.warning(f"Compliance generation failed: {e}")
                compliance_explanation = "Compliance review required but detailed analysis unavailable."
        
        # Build response
        should_approve = risk_result.risk_level in ["Low"]
        requires_review = risk_result.risk_level in ["Medium", "High", "Critical"]
        
        logger.info(
            f"Transaction {transaction_id} analyzed: "
            f"risk={risk_result.risk_level}, approve={should_approve}"
        )
        
        return RiskResponse(
            transaction_id=transaction_id,
            risk_score=risk_result.risk_score,
            risk_level=risk_result.risk_level,
            should_approve=should_approve,
            requires_review=requires_review,
            compliance_explanation=compliance_explanation
        )
        
    except Exception as e:
        logger.error(f"Transaction analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    transaction: TransactionCreate,
    risk_engine: RiskEngineProtocol = Depends(get_risk_engine)
) -> TransactionResponse:
    """
    Create a new transaction with risk assessment.
    
    Args:
        transaction: Transaction creation request
        risk_engine: Injected risk engine
        
    Returns:
        TransactionResponse with risk assessment
    """
    try:
        transaction_id = str(uuid4())
        
        # Convert to full Transaction model for risk assessment
        full_transaction = Transaction(
            transaction_id=transaction_id,
            user_id=transaction.user_id,
            amount=transaction.amount,
            currency=transaction.currency,
            transaction_type=transaction.transaction_type,
            description=transaction.description,
            recipient_account=transaction.recipient_account,
            sender_account=transaction.sender_account,
            country=transaction.country,
            merchant_type=transaction.merchant_type,
            device_risk_score=transaction.device_risk_score
        )
        
        # Assess risk (async)
        risk_result = await risk_engine.assess_risk_async(full_transaction)
        
        # Store transaction
        transactions_db[transaction_id] = {
            "id": transaction_id,
            "user_id": full_transaction.user_id,
            "amount": full_transaction.amount,
            "currency": full_transaction.currency,
            "transaction_type": full_transaction.transaction_type.value,
            "description": full_transaction.description,
            "recipient_account": full_transaction.recipient_account,
            "sender_account": full_transaction.sender_account,
            "country": full_transaction.country,
            "merchant_type": full_transaction.merchant_type,
            "device_risk_score": full_transaction.device_risk_score,
            "timestamp": full_transaction.timestamp.isoformat(),
            "risk_score": risk_result.risk_score,
            "risk_level": risk_result.risk_level
        }
        
        logger.info(f"Transaction {transaction_id} created with risk level: {risk_result.risk_level}")
        
        return TransactionResponse(
            id=transaction_id,
            user_id=full_transaction.user_id,
            amount=full_transaction.amount,
            currency=full_transaction.currency,
            transaction_type=full_transaction.transaction_type,
            description=full_transaction.description,
            recipient_account=full_transaction.recipient_account,
            sender_account=full_transaction.sender_account,
            country=full_transaction.country,
            merchant_type=full_transaction.merchant_type,
            device_risk_score=full_transaction.device_risk_score,
            timestamp=full_transaction.timestamp,
            risk_score=risk_result.risk_score,
            risk_level=risk_result.risk_level
        )
        
    except Exception as e:
        logger.error(f"Transaction creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Creation failed: {str(e)}")


@router.get("/", response_model=List[TransactionResponse])
async def list_transactions(
    limit: int = 100,
    offset: int = 0
) -> List[TransactionResponse]:
    """
    List all transactions with pagination.
    
    Args:
        limit: Maximum number of transactions to return
        offset: Number of transactions to skip
        
    Returns:
        List of TransactionResponse
    """
    transactions = list(transactions_db.values())
    transactions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    paginated = transactions[offset:offset + limit]
    
    return [
        TransactionResponse(
            id=tx["id"],
            user_id=tx["user_id"],
            amount=tx["amount"],
            currency=tx.get("currency", "USD"),
            transaction_type=tx.get("transaction_type", "transfer"),
            description=tx.get("description"),
            recipient_account=tx.get("recipient_account", ""),
            sender_account=tx.get("sender_account", ""),
            country=tx.get("country", "India"),
            merchant_type=tx.get("merchant_type", "retail"),
            device_risk_score=tx.get("device_risk_score", 0.0),
            timestamp=tx.get("timestamp"),
            risk_score=tx.get("risk_score"),
            risk_level=tx.get("risk_level")
        )
        for tx in paginated
    ]


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str) -> TransactionResponse:
    """
    Get a specific transaction by ID.
    
    Args:
        transaction_id: Transaction ID
        
    Returns:
        TransactionResponse
        
    Raises:
        HTTPException: If transaction not found
    """
    if transaction_id not in transactions_db:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    tx = transactions_db[transaction_id]
    return TransactionResponse(
        id=tx["id"],
        user_id=tx["user_id"],
        amount=tx["amount"],
        currency=tx.get("currency", "USD"),
        transaction_type=tx.get("transaction_type", "transfer"),
        description=tx.get("description"),
        recipient_account=tx.get("recipient_account", ""),
        sender_account=tx.get("sender_account", ""),
        country=tx.get("country", "India"),
        merchant_type=tx.get("merchant_type", "retail"),
        device_risk_score=tx.get("device_risk_score", 0.0),
        timestamp=tx.get("timestamp"),
        risk_score=tx.get("risk_score"),
        risk_level=tx.get("risk_level")
    )


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: str) -> dict:
    """
    Delete a transaction.
    
    Args:
        transaction_id: Transaction ID
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If transaction not found
    """
    if transaction_id not in transactions_db:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    del transactions_db[transaction_id]
    logger.info(f"Transaction {transaction_id} deleted")
    
    return {"message": "Transaction deleted", "id": transaction_id}
