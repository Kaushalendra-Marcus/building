from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal


class QueryCreate(BaseModel):
    query: str


class QueryResponse(BaseModel):
    id: UUID
    query: str
    response: Optional[str] = None
    intent: Optional[str] = None
    execution_time: Optional[Decimal] = None
    created_at: datetime

    class Config:
        from_attributes = True
