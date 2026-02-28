"""Risk Engine Service - Rule-based risk assessment."""
from app.models.transaction_model import TransactionCreate
from app.models.risk_response_model import RiskResult, RiskLevel
from app.config import settings


class RiskEngine:
    """Rule-based risk engine for transaction assessment."""
    
    def __init__(self):
        self.threshold_high = settings.risk_threshold_high
        self.threshold_medium = settings.risk_threshold_medium
    
    def assess_risk(self, transaction: TransactionCreate) -> RiskResult:
        """Assess transaction risk using rule-based logic."""
        factors = []
        recommendations = []
        risk_score = 0
        
        # Rule 1: Amount-based risk
        if transaction.amount > 10000:
            risk_score += 30
            factors.append("High transaction amount")
            recommendations.append("Verify source of funds")
        elif transaction.amount > 5000:
            risk_score += 15
            factors.append("Medium transaction amount")
        
        # Rule 2: Transaction type risk
        if transaction.transaction_type.value == "transfer":
            risk_score += 10
            factors.append("Transfer transaction")
            recommendations.append("Verify recipient identity")
        
        # Rule 3: Cross-border risk (simplified)
        if transaction.currency != "USD":
            risk_score += 15
            factors.append("Foreign currency transaction")
        
        # Cap risk score
        risk_score = min(100, risk_score)
        
        # Determine risk level
        if risk_score >= self.threshold_high:
            risk_level = RiskLevel.HIGH
        elif risk_score >= self.threshold_medium:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        return RiskResult(
            risk_score=risk_score,
            risk_level=risk_level,
            factors=factors,
            recommendations=recommendations
        )
