from sqlalchemy import Column, DateTime, Numeric, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    utr = Column(String(100), unique=True, index=True, nullable=False)

    amount = Column(Numeric(10, 2), nullable=False)

    status = Column(String(50), default="pending", nullable=False)

    admin_note = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    verified_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="payments")