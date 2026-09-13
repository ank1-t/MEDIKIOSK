"""
x402 Payment-Protected Endpoints on Algorand TestNet
Enforces HTTP 402 Payment Required status and validates payment via GoPlausible Facilitator
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Header, Response, status, HTTPException
from app.services.x402_service import X402Service, ALGORAND_TESTNET_CAIP2, USDC_TESTNET_ASA_ID

router = APIRouter(prefix="/x402", tags=["x402 Algorand Payments"])

@router.get("/config")
async def get_x402_config():
    """Returns the x402 Algorand TestNet configuration and GoPlausible facilitator settings."""
    challenge = X402Service.create_payment_challenge(endpoint="/api/v1/x402/verify-intake")
    return {
        "status": "active",
        "network": "Algorand TestNet",
        "caip2": ALGORAND_TESTNET_CAIP2,
        "usdc_asa_id": USDC_TESTNET_ASA_ID,
        "facilitator_name": "GoPlausible",
        "challenge": challenge,
        "explorer": "https://lora.algokit.io/testnet"
    }


@router.post("/challenge")
async def create_challenge(payload: Optional[Dict[str, Any]] = None):
    """Generates an explicit HTTP 402 challenge for an intake consultation or service."""
    service_name = (payload or {}).get("service", "Clinical AI Consultation & Summary")
    price = (payload or {}).get("price", "$0.005")
    challenge = X402Service.create_payment_challenge(
        endpoint="/api/v1/x402/verify-intake",
        price_usd=price,
        description=f"MediKiosk {service_name} — Pay {price} USDC on Algorand TestNet"
    )
    return Response(
        content=__import__("json").dumps(challenge),
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        media_type="application/json",
        headers={
            "Payment-Required": "x402",
            "X-Facilitator": "GoPlausible",
            "X-Network": "Algorand-TestNet"
        }
    )


@router.post("/verify-intake")
async def verify_intake_payment(
    payload: Optional[Dict[str, Any]] = None,
    payment_signature: Optional[str] = Header(None, alias="payment-signature"),
    x_payment: Optional[str] = Header(None, alias="x-payment")
):
    """
    Validates payment and issues receipt on Algorand TestNet.
    If no signature is provided, returns HTTP 402 Payment Required.
    """
    sig = payment_signature or x_payment or (payload or {}).get("signature") or (payload or {}).get("tx_id")
    
    # Check if client hasn't paid yet
    if not sig and not (payload or {}).get("auto_settle"):
        challenge = X402Service.create_payment_challenge(endpoint="/api/v1/x402/verify-intake")
        return Response(
            content=__import__("json").dumps(challenge),
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            media_type="application/json",
            headers={"Payment-Required": "x402", "X-Facilitator": "GoPlausible"}
        )

    # Validate and settle
    verification = await X402Service.verify_payment(payment_signature=sig, tx_id=(payload or {}).get("tx_id"))
    return {
        "success": True,
        "message": "Payment verified via GoPlausible Facilitator on Algorand TestNet",
        "verification": verification
    }
