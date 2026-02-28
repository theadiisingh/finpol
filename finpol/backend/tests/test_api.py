"""Tests for API endpoints."""
import pytest
from httpx import AsyncClient
import sys
import os

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app


class TestAPI:
    """Test cases for API endpoints."""
    
    @pytest.fixture
    def anyio_backend(self):
        return "asyncio"
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test health check endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Test root endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/")
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_transaction_endpoint(self):
        """Test transaction creation endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            transaction_data = {
                "user_id": "user-123",
                "amount": 1000,
                "currency": "USD",
                "transaction_type": "transfer",
                "recipient_account": "ACC123456",
                "sender_account": "ACC789012",
                "country": "India",
                "merchant_type": "retail",
                "device_risk_score": 0.2
            }
            response = await client.post("/api/v1/transactions", json=transaction_data)
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert data["amount"] == 1000
    
    @pytest.mark.asyncio
    async def test_analyze_endpoint(self):
        """Test transaction analyze endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            transaction_data = {
                "transaction_id": "tx-001",
                "user_id": "user-123",
                "amount": 5000,
                "country": "India",
                "merchant_type": "retail",
                "device_risk_score": 0.3,
                "timestamp": "2024-01-01T00:00:00"
            }
            response = await client.post("/api/v1/transactions/analyze", json=transaction_data)
            assert response.status_code == 200
            data = response.json()
            assert "risk_score" in data
            assert "risk_level" in data
