from sqlalchemy import (
    Column,
    DateTime,
    Numeric,
    String,
    UUID,
    ForeignKey,
    Enum,
)
import uuid
from sqlalchemy.sql import func
from app.db.database import Base


class Payment(Base):
    __tablename__ = "payments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    utr = Column(String(100), unique=True, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(
        Enum("pending", "verified", "rejected", name="payment_status_enum"),
        default="pending",
        nullable=False,
    )
    note = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
