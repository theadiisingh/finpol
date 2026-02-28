"""Risk Engine Service - Rule-based risk assessment with async support.

This module provides:
- Rule-based risk assessment
- Async evaluation support for scalability
- Easy extension for ML-based risk models
- Clear abstraction layer for future ML integration
"""
from app.models.transaction_model import Transaction
from app.models.risk_response_model import RiskResult, RiskResponse
from app.config import settings
from typing import List, Dict, Any, Optional
from enum import Enum
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Risk severity levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class RiskRule(ABC):
    """Abstract base class for risk rules.
    
    Allows easy extension with ML-based rules in the future.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Rule name for logging."""
        pass
    
    @abstractmethod
    def evaluate(self, transaction: Transaction) -> Optional[tuple[str, RiskLevel]]:
        """Evaluate the rule against a transaction."""
        pass


class RiskEngineProtocol(ABC):
    """Abstract protocol for Risk Engine.
    
    Allows swapping implementations (rule-based, ML-based, hybrid).
    """
    
    @abstractmethod
    def evaluate(self, transaction: Transaction) -> Dict[str, Any]:
        """Synchronous risk evaluation."""
        pass
    
    @abstractmethod
    async def evaluate_async(self, transaction: Transaction) -> Dict[str, Any]:
        """Asynchronous risk evaluation."""
        pass
    
    @abstractmethod
    def assess_risk(self, transaction: Transaction) -> RiskResult:
        """Assess risk and return structured result."""
        pass


class RiskEngine(RiskEngineProtocol):
    """
    Rule-based risk engine for transaction assessment.
    
    Supports:
    - Sync and async evaluation
    - Custom rule addition
    - Easy ML model integration via RiskRule abstraction
    """
    
    def __init__(
        self,
        threshold_high: int = None,
        threshold_medium: int = None
    ):
        """
        Initialize Risk Engine.
        
        Args:
            threshold_high: High risk threshold (0-100)
            threshold_medium: Medium risk threshold (0-100)
        """
        self._threshold_high = threshold_high or settings.risk_threshold_high
        self._threshold_medium = threshold_medium or settings.risk_threshold_medium
        
        # Initialize built-in rules
        self._rules: List[RiskRule] = [
            HighAmountRule(),
            CryptoExchangeRule(),
            ForeignHighValueRule(),
            HighDeviceRiskRule(),
        ]
        
        logger.info(
            f"RiskEngine initialized with {len(self._rules)} rules, "
            f"thresholds: high={self._threshold_high}, medium={self._threshold_medium}"
        )
    
    def evaluate(self, transaction: Transaction) -> Dict[str, Any]:
        """
        Synchronous risk evaluation.
        
        Args:
            transaction: Transaction to evaluate
            
        Returns:
            Dictionary with risk_score, risk_level, and reasons
        """
        return self._evaluate_internal(transaction)
    
    async def evaluate_async(self, transaction: Transaction) -> Dict[str, Any]:
        """
        Asynchronous risk evaluation.
        
        Allows for future ML model integration that may require
        async operations (GPU inference, external APIs, etc.)
        
        Args:
            transaction: Transaction to evaluate
            
        Returns:
            Dictionary with risk_score, risk_level, and reasons
        """
        # For now, delegate to sync version
        # In future, this can integrate with async ML models
        logger.debug(f"Async evaluation for transaction {transaction.transaction_id}")
        return self._evaluate_internal(transaction)
    
    def _evaluate_internal(self, transaction: Transaction) -> Dict[str, Any]:
        """Internal evaluation logic."""
        reasons: List[str] = []
        severity_order = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        current_level = RiskLevel.LOW
        
        # Apply all rules - highest severity wins
        for rule in self._rules:
            try:
                rule_result = rule.evaluate(transaction)
                if rule_result:
                    reason, level = rule_result
                    reasons.append(reason)
                    if severity_order.index(level) > severity_order.index(current_level):
                        current_level = level
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {e}")
        
        return {
            "risk_score": current_level.value,
            "risk_level": current_level,
            "reasons": reasons
        }
    
    def assess_risk(self, transaction: Transaction) -> RiskResult:
        """
        Assess risk and return RiskResult model.
        
        Args:
            transaction: Transaction to evaluate
            
        Returns:
            RiskResult with risk assessment
        """
        evaluation = self.evaluate(transaction)
        
        # Convert risk level to numeric score
        risk_score = self._level_to_score(evaluation["risk_level"])
        
        # Generate recommendations based on risk factors
        recommendations = self._generate_recommendations(
            evaluation["risk_level"],
            evaluation["reasons"]
        )
        
        logger.info(
            f"Risk assessment for transaction {getattr(transaction, 'transaction_id', 'unknown')}: "
            f"level={evaluation['risk_level'].value}, score={risk_score}"
        )
        
        return RiskResult(
            risk_score=risk_score,
            risk_level=evaluation["risk_level"].value,
            factors=evaluation["reasons"],
            recommendations=recommendations
        )
    
    async def assess_risk_async(self, transaction: Transaction) -> RiskResult:
        """
        Asynchronous risk assessment.
        
        Args:
            transaction: Transaction to evaluate
            
        Returns:
            RiskResult with risk assessment
        """
        evaluation = await self.evaluate_async(transaction)
        
        risk_score = self._level_to_score(evaluation["risk_level"])
        recommendations = self._generate_recommendations(
            evaluation["risk_level"],
            evaluation["reasons"]
        )
        
        return RiskResult(
            risk_score=risk_score,
            risk_level=evaluation["risk_level"].value,
            factors=evaluation["reasons"],
            recommendations=recommendations
        )
    
    def _level_to_score(self, level: RiskLevel) -> int:
        """Convert risk level to numeric score."""
        mapping = {
            RiskLevel.LOW: 25,
            RiskLevel.MEDIUM: 60,
            RiskLevel.HIGH: 85,
            RiskLevel.CRITICAL: 95
        }
        return mapping.get(level, 0)
    
    def _generate_recommendations(self, level: RiskLevel, reasons: List[str]) -> List[str]:
        """Generate recommendations based on risk factors."""
        recommendations = []
        
        if level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("Transaction requires manual review")
            recommendations.append("Verify customer identity before processing")
        
        if any("amount" in r.lower() for r in reasons):
            recommendations.append("Confirm source of funds")
        
        if any("crypto" in r.lower() for r in reasons):
            recommendations.append("Ensure compliance with crypto regulations")
        
        if any("foreign" in r.lower() or "country" in r.lower() for r in reasons):
            recommendations.append("Verify cross-border compliance requirements")
        
        if any("device" in r.lower() for r in reasons):
            recommendations.append("Request additional device verification")
        
        if not recommendations:
            recommendations.append("Transaction can proceed with standard processing")
        
        return recommendations
    
    def create_risk_response(
        self,
        assessment: RiskResult,
        transaction_id: str,
        compliance_explanation: Optional[str] = None
    ) -> RiskResponse:
        """
        Create a RiskResponse from assessment.
        
        Args:
            assessment: RiskResult from assess_risk
            transaction_id: Transaction ID
            compliance_explanation: Optional compliance explanation
            
        Returns:
            RiskResponse model
        """
        should_approve = assessment.risk_level in ["Low"]
        requires_review = assessment.risk_level in ["Medium", "High", "Critical"]
        
        return RiskResponse(
            transaction_id=transaction_id,
            risk_score=assessment.risk_score,
            risk_level=assessment.risk_level,
            should_approve=should_approve,
            requires_review=requires_review,
            compliance_explanation=compliance_explanation
        )
    
    def add_rule(self, rule: RiskRule) -> None:
        """
        Add a custom rule to the engine.
        
        Args:
            rule: RiskRule implementation
        """
        self._rules.append(rule)
        logger.info(f"Added custom rule: {rule.name}")


# ============================================================
# Built-in Risk Rules
# ============================================================


class HighAmountRule(RiskRule):
    """Rule: amount > 1000000 → High"""
    
    @property
    def name(self) -> str:
        return "HighAmountRule"
    
    def evaluate(self, transaction: Transaction) -> Optional[tuple[str, RiskLevel]]:
        if transaction.amount > 1000000:
            return "Transaction amount exceeds 1,000,000", RiskLevel.HIGH
        return None


class CryptoExchangeRule(RiskRule):
    """Rule: merchant_type == 'crypto_exchange' → Medium"""
    
    @property
    def name(self) -> str:
        return "CryptoExchangeRule"
    
    def evaluate(self, transaction: Transaction) -> Optional[tuple[str, RiskLevel]]:
        if transaction.merchant_type == "crypto_exchange":
            return "Crypto exchange merchant type", RiskLevel.MEDIUM
        return None


class ForeignHighValueRule(RiskRule):
    """Rule: country != 'India' AND amount > 500000 → High"""
    
    @property
    def name(self) -> str:
        return "ForeignHighValueRule"
    
    def evaluate(self, transaction: Transaction) -> Optional[tuple[str, RiskLevel]]:
        if transaction.country != "India" and transaction.amount > 500000:
            return f"High-value transaction ({transaction.amount}) from non-India country", RiskLevel.HIGH
        return None


class HighDeviceRiskRule(RiskRule):
    """Rule: device_risk_score > 0.7 → Medium"""
    
    @property
    def name(self) -> str:
        return "HighDeviceRiskRule"
    
    def evaluate(self, transaction: Transaction) -> Optional[tuple[str, RiskLevel]]:
        if transaction.device_risk_score > 0.7:
            return f"High device risk score ({transaction.device_risk_score})", RiskLevel.MEDIUM
        return None
