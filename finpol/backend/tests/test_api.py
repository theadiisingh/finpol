"""Tests for API endpoints."""
import pytest
from httpx import AsyncClient
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
            response = await client.get("/api/v1/health")
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
                "sender_account": "ACC789012"
            }
            response = await client.post("/api/v1/transactions", json=transaction_data)
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert data["amount"] == 1000
