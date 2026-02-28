"""Tests for Risk Engine service."""
import pytest
from datetime import datetime
from app.services.risk_engine import RiskEngine, RiskLevel
from app.models.transaction_model import Transaction, TransactionType


class TestRiskEngine:
    """Test cases for RiskEngine."""
    
    @pytest.fixture
    def risk_engine(self):
        """Create risk engine instance."""
        return RiskEngine()
    
    @pytest.fixture
    def sample_transaction(self):
        """Create sample transaction."""
        return Transaction(
            transaction_id="test-001",
            user_id="user-123",
            amount=100,
            currency="USD",
            transaction_type=TransactionType.TRANSFER,
            description="Test transfer",
            recipient_account="ACC123456",
            sender_account="ACC789012",
            country="India",
            merchant_type="retail",
            device_risk_score=0.3,
            timestamp=datetime.now()
        )
    
    def test_assess_low_risk_transaction(self, risk_engine, sample_transaction):
        """Test assessment of low risk transaction."""
        assessment = risk_engine.assess_risk(sample_transaction)
        
        assert assessment.risk_score < 50
        assert assessment.risk_level in ["Low", "Medium"]
    
    def test_assess_high_amount_transaction(self, risk_engine, sample_transaction):
        """Test assessment of high amount transaction."""
        sample_transaction.amount = 2000000
        assessment = risk_engine.assess_risk(sample_transaction)
        
        assert any("amount" in factor.lower() for factor in assessment.factors)
        assert assessment.risk_level == "High"
    
    def test_assess_crypto_merchant(self, risk_engine, sample_transaction):
        """Test assessment of crypto merchant type."""
        sample_transaction.merchant_type = "crypto_exchange"
        assessment = risk_engine.assess_risk(sample_transaction)
        
        assert any("crypto" in factor.lower() for factor in assessment.factors)
    
    def test_create_risk_response(self, risk_engine, sample_transaction):
        """Test risk response creation."""
        assessment = risk_engine.assess_risk(sample_transaction)
        response = risk_engine.create_risk_response(
            assessment=assessment,
            transaction_id=sample_transaction.transaction_id
        )
        
        assert response.transaction_id == sample_transaction.transaction_id
        assert response.should_approve is not None
        assert response.requires_review is not None
