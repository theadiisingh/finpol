"""Transaction models with Pydantic v2 validation.

This module provides:
- Transaction model for API requests/responses
- Transaction creation model
- Transaction type enumeration
- Proper validation and typing
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    """Transaction type enumeration."""
    TRANSFER = "transfer"
    PAYMENT = "payment"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"


class Transaction(BaseModel):
    """
    Transaction model with validation.
    
    Used for transaction analysis and risk assessment.
    """
    
    transaction_id: str = Field(default_factory=lambda: "TXN-" + str(datetime.now().timestamp()))
    user_id: str = Field(..., min_length=1, description="User identifier")
    amount: float = Field(..., gt=0, description="Transaction amount")
    currency: str = Field(default="USD", description="Currency code")
    country: str = Field(default="India", description="Country code")
    merchant_type: str = Field(default="retail", description="Merchant category")
    device_risk_score: float = Field(..., ge=0.0, le=1.0, description="Device risk score")
    timestamp: datetime = Field(default_factory=datetime.now, description="Transaction timestamp")
    
    # Additional fields
    transaction_type: Optional[TransactionType] = Field(default=TransactionType.TRANSFER, description="Transaction type")
    description: Optional[str] = Field(default=None, description="Transaction description")
    recipient_account: Optional[str] = Field(default=None, description="Recipient account")
    sender_account: Optional[str] = Field(default=None, description="Sender account")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "transaction_id": "TXN-123456",
                "user_id": "user-123",
                "amount": 5000.00,
                "currency": "USD",
                "country": "India",
                "merchant_type": "retail",
                "device_risk_score": 0.3,
                "transaction_type": "transfer"
            }
        }
    }


class TransactionCreate(BaseModel):
    """
    Transaction creation model for API requests.
    """
    
    user_id: str = Field(..., min_length=1, description="User identifier")
    amount: float = Field(..., gt=0, description="Transaction amount")
    currency: str = Field(default="USD", description="Currency code")
    transaction_type: TransactionType = Field(default=TransactionType.TRANSFER, description="Transaction type")
    description: Optional[str] = Field(default=None, description="Transaction description")
    recipient_account: str = Field(..., min_length=1, description="Recipient account number")
    sender_account: str = Field(..., min_length=1, description="Sender account number")
    country: str = Field(default="India", description="Country code")
    merchant_type: str = Field(default="retail", description="Merchant category")
    device_risk_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Device risk score")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "user-123",
                "amount": 5000.00,
                "currency": "USD",
                "transaction_type": "transfer",
                "description": "Payment for services",
                "recipient_account": "ACC123456",
                "sender_account": "ACC789012",
                "country": "India",
                "merchant_type": "retail",
                "device_risk_score": 0.3
            }
        }
    }


class TransactionResponse(BaseModel):
    """
    Transaction response model with risk assessment.
    """
    
    id: str = Field(..., description="Transaction ID")
    user_id: str = Field(..., description="User identifier")
    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(default="USD", description="Currency code")
    transaction_type: TransactionType = Field(default=TransactionType.TRANSFER, description="Transaction type")
    description: Optional[str] = Field(default=None, description="Transaction description")
    recipient_account: str = Field(default="", description="Recipient account")
    sender_account: str = Field(default="", description="Sender account")
    country: str = Field(default="India", description="Country")
    merchant_type: str = Field(default="retail", description="Merchant category")
    device_risk_score: float = Field(default=0.0, description="Device risk score")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp")
    
    # Risk assessment fields
    risk_score: Optional[int] = Field(default=None, description="Risk score (0-100)")
    risk_level: Optional[str] = Field(default=None, description="Risk level")
    
    model_config = {
        "from_attributes": True
    }
