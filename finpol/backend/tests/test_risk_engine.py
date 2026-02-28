"""Tests for Risk Engine service."""
import pytest
from app.services.risk_engine import RiskEngine
from app.models.transaction import Transaction, TransactionType
from app.models.risk import RiskLevel


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
            id="test-001",
            user_id="user-123",
            amount=5000,
            currency="USD",
            transaction_type=TransactionType.TRANSFER,
            description="Test transfer",
            recipient_account="ACC123456",
            sender_account="ACC789012"
        )
    
    def test_assess_low_risk_transaction(self, risk_engine, sample_transaction):
        """Test assessment of low risk transaction."""
        sample_transaction.amount = 100
        assessment = risk_engine.assess_risk(sample_transaction)
        
        assert assessment.risk_score < 50
        assert assessment.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]
    
    def test_assess_high_amount_transaction(self, risk_engine, sample_transaction):
        """Test assessment of high amount transaction."""
        sample_transaction.amount = 50000
        assessment = risk_engine.assess_risk(sample_transaction)
        
        assert any("amount" in factor.lower() for factor in assessment.factors)
    
    def test_assess_transfer_transaction(self, risk_engine, sample_transaction):
        """Test assessment of transfer transaction."""
        sample_transaction.transaction_type = TransactionType.TRANSFER
        assessment = risk_engine.assess_risk(sample_transaction)
        
        assert any("transfer" in factor.lower() for factor in assessment.factors)
    
    def test_create_risk_response_approve(self, risk_engine, sample_transaction):
        """Test risk response for low risk."""
        assessment = risk_engine.assess_risk(sample_transaction)
        response = risk_engine.create_risk_response(assessment)
        
        assert response.should_approve is not None
        assert response.requires_review is not None
