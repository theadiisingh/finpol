"""Risk Engine Service - Rule-based risk assessment."""
from app.models.transaction_model import Transaction
from typing import List, Dict, Any
from enum import Enum


class RiskLevel(str, Enum):
    """Risk severity levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class RiskEngine:
    """Rule-based risk engine for transaction assessment."""
    
    def __init__(self):
        self._rules: List[callable] = [
            self._rule_high_amount,
            self._rule_crypto_exchange,
            self._rule_foreign_high_value,
            self._rule_high_device_risk,
        ]
    
    def evaluate(self, transaction: Transaction) -> Dict[str, Any]:
        """
        Evaluate transaction risk.
        
        Args:
            transaction: Transaction to evaluate
            
        Returns:
            Dictionary with risk_score and reasons
        """
        reasons: List[str] = []
        severity_order = [RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.LOW]
        current_level = RiskLevel.LOW
        
        # Apply all rules - highest severity wins
        for rule in self._rules:
            rule_result = rule(transaction)
            if rule_result:
                reason, level = rule_result
                reasons.append(reason)
                if severity_order.index(level) > severity_order.index(current_level):
                    current_level = level
        
        return {
            "risk_score": current_level.value,
            "reasons": reasons
        }
    
    @staticmethod
    def _rule_high_amount(transaction: Transaction) -> tuple[str, RiskLevel] | None:
        """Rule: amount > 1000000 → High"""
        if transaction.amount > 1000000:
            return "Transaction amount exceeds 1,000,000", RiskLevel.HIGH
        return None
    
    @staticmethod
    def _rule_crypto_exchange(transaction: Transaction) -> tuple[str, RiskLevel] | None:
        """Rule: merchant_type == 'crypto_exchange' → Medium"""
        if transaction.merchant_type == "crypto_exchange":
            return "Crypto exchange merchant type", RiskLevel.MEDIUM
        return None
    
    @staticmethod
    def _rule_foreign_high_value(transaction: Transaction) -> tuple[str, RiskLevel] | None:
        """Rule: country != 'India' AND amount > 500000 → High"""
        if transaction.country != "India" and transaction.amount > 500000:
            return f"High-value transaction ({transaction.amount}) from non-India country", RiskLevel.HIGH
        return None
    
    @staticmethod
    def _rule_high_device_risk(transaction: Transaction) -> tuple[str, RiskLevel] | None:
        """Rule: device_risk_score > 0.7 → Medium"""
        if transaction.device_risk_score > 0.7:
            return f"High device risk score ({transaction.device_risk_score})", RiskLevel.MEDIUM
        return None
    
    def add_rule(self, rule: callable) -> None:
        """
        Add a custom rule to the engine.
        
        Args:
            rule: Callable that takes Transaction and returns (reason, RiskLevel) or None
        """
        self._rules.append(rule)
