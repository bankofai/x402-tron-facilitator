from typing import Literal
from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from x402_tron.facilitator import X402Facilitator
from x402_tron.mechanisms.facilitator import UptoTronFacilitatorMechanism
from x402_tron.signers.facilitator import TronFacilitatorSigner
from .config import PRIVATE_KEY


app = FastAPI()

# Initialize facilitator
facilitator = X402Facilitator()
signer = TronFacilitatorSigner(private_key=PRIVATE_KEY)
mechanism = UptoTronFacilitatorMechanism(signer=signer)

from typing import Any, Optional
from pydantic import BaseModel
from x402_tron.types import PaymentPayload, PaymentRequirements

class VerifySettleRequest(BaseModel):
    paymentPayload: PaymentPayload
    paymentRequirements: PaymentRequirements

class FeeQuoteRequest(BaseModel):
    accept: PaymentRequirements
    paymentPermitContext: Optional[dict[str, Any]] = None

networks = ["tron:nile", "tron:mainnet", "tron:shasta"]
facilitator.register(networks, mechanism)

@app.get("/supported")
async def supported():
    return facilitator.supported()

@app.post("/verify")
async def verify(request: VerifySettleRequest):
    return await facilitator.verify(request.paymentPayload, request.paymentRequirements)

@app.post("/settle")
async def settle(request: VerifySettleRequest):
    return await facilitator.settle(request.paymentPayload, request.paymentRequirements)

@app.post("/fee/quote")
async def fee_quote(request: FeeQuoteRequest):
    return await facilitator.fee_quote(request.accept, request.paymentPermitContext)