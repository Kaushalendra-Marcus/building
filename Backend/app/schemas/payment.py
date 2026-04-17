from pydantic import BaseModel, field_validator
from uuid import UUID
from typing import Optional
from datetime import datetime
from decimal import Decimal


class CreatePayment(BaseModel):
    utr: str
    amount: Decimal

    @field_validator("utr")
    @classmethod
    def validate_utr(cls, v):
        if len(v) < 12 or len(v) > 22:
            raise ValueError("Invalid UTR number")
        return v


class PaymentVerify(BaseModel):
    utr: str


class PaymentReject(BaseModel):
    utr: str
    note: Optional[str] = None


class PaymentResponse(BaseModel):
    id: UUID
    utr: str
    amount: float
    status: str
    note: Optional[str] = None
    created_at: datetime
    verified_at: Optional[datetime] = None

    class Config:
        from_attributes = True
