"""Risk response model."""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class RiskLevel(str):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskResult(BaseModel):
    """Risk assessment result."""
    risk_score: int
    risk_level: str
    factors: List[str] = []
    recommendations: List[str] = []


class RiskResponse(BaseModel):
    """Risk response model."""
    transaction_id: str
    risk_score: int
    risk_level: str
    should_approve: bool
    requires_review: bool


class ComplianceReport(BaseModel):
    """Compliance report model."""
    transaction_id: str
    compliance_status: str
    regulations_applied: List[str] = []
    violations: List[str] = []
    recommendations: List[str] = []
    llm_analysis: Optional[str] = None
    timestamp: datetime
