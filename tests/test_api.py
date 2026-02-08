
import pytest
import json
from datetime import datetime
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_get_supported(client, mocker):
    """Test /supported endpoint"""
    # Mock x402_facilitator.supported
    mock_supported = mocker.patch("main.x402_facilitator.supported", return_value={"pricing": "flat"})
    
    response = await client.get("/supported")
    assert response.status_code == 200
    assert response.json() == {"pricing": "flat"}

@pytest.mark.asyncio
async def test_get_payment_success(client, mock_db):
    """Test /payments/{payment_id} endpoint - Success state"""
    # Mock database record
    mock_record = MagicMock()
    mock_record.payment_id = "pay-123"
    mock_record.tx_hash = "0xhash"
    mock_record.status = "success"
    mock_record.created_at = datetime.now()
    
    mock_db["get"].return_value = mock_record
    
    response = await client.get("/payments/pay-123")
    assert response.status_code == 200
    data = response.json()
    assert data["paymentId"] == "pay-123"
    assert data["txHash"] == "0xhash"

@pytest.mark.asyncio
async def test_get_payment_not_found(client, mock_db):
    """Test /payments/{payment_id} endpoint - Not found state"""
    mock_db["get"].return_value = None
    
    response = await client.get("/payments/non-existent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"

@pytest.mark.asyncio
async def test_rate_limiting_trigger(client, mocker):
    """Verify rate limiting trigger logic (Anonymous user 1/min)"""
    # Mock authentication state as False
    mocker.patch("auth.get_remote_address", return_value="1.2.3.4")
    mocker.patch("main.x402_facilitator.supported", return_value={})
    
    # First request succeeds
    resp1 = await client.get("/supported")
    assert resp1.status_code == 200
    
    # Second request should trigger 429
    # Note: Middleware is active in pytest environment, triggering slowapi logic
    resp2 = await client.get("/supported")
    assert resp2.status_code == 429
    assert "Rate limit exceeded" in resp2.json()["error"]

from unittest.mock import MagicMock
