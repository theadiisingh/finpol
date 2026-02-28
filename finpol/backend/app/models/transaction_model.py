"""Transaction model."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    TRANSFER = "transfer"
    PAYMENT = "payment"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"


class Transaction(BaseModel):
    """Transaction model with validation."""
    
    transaction_id: str
    user_id: str
    amount: float = Field(..., gt=0)
    country: str
    merchant_type: str
    device_risk_score: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime


class TransactionCreate(BaseModel):
    """Transaction creation model."""
    user_id: str
    amount: float = Field(..., gt=0)
    currency: str = "USD"
    transaction_type: TransactionType
    description: Optional[str] = None
    recipient_account: str
    sender_account: str


class TransactionResponse(BaseModel):
    """Transaction response model."""
    id: str
    user_id: str
    amount: float
    currency: str
    transaction_type: TransactionType
    description: Optional[str]
    recipient_account: str
    sender_account: str
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
