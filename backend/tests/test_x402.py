"""
Tests for x402 Algorand Micropayments & GoPlausible Facilitator
Verifies:
- GET /api/v1/x402/config
- POST /api/v1/x402/challenge returns HTTP 402 Payment Required
- POST /api/v1/x402/verify-intake without payment returns HTTP 402
- POST /api/v1/x402/verify-intake with payment signature validates and provides Lora Algokit URL
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_x402_config():
    res = client.get("/api/v1/x402/config")
    assert res.status_code == 200
    data = res.json()
    assert data["network"] == "Algorand TestNet"
    assert data["facilitator_name"] == "GoPlausible"
    assert "https://lora.algokit.io/testnet" in data["explorer"]
    assert data["challenge"]["status"] == 402


def test_x402_challenge_endpoint():
    res = client.post("/api/v1/x402/challenge", json={"service": "AI Intake Summary", "price": "$0.005"})
    assert res.status_code == 402
    data = res.json()
    assert data["status"] == 402
    assert data["protocol"] == "x402"
    assert data["accepts"][0]["price"] == "$0.005"
    assert data["facilitator"]["type"] == "goplausible"


def test_x402_payment_verification_and_lora_link():
    # 1. Unpaid request returns 402
    unpaid_res = client.post("/api/v1/x402/verify-intake")
    assert unpaid_res.status_code == 402

    # 2. Paid request with signature succeeds and produces Lora Algokit explorer URL
    paid_res = client.post(
        "/api/v1/x402/verify-intake",
        headers={"payment-signature": "SIG-ALGO-TESTNET-DEMO-99128"},
        json={"tx_id": "7AB619C0E28564D12F5B612C9"}
    )
    assert paid_res.status_code == 200
    data = paid_res.json()
    assert data["success"] is True
    verification = data["verification"]
    assert verification["status"] == "settled"
    assert verification["network"] == "Algorand TestNet"
    assert verification["facilitator"] == "GoPlausible"
    assert "https://lora.algokit.io/testnet/transaction/7AB619C0E28564D12F5B612C9" == verification["lora_url"]
