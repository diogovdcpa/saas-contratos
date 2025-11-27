from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.db import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    provider_name = Column(String(200), nullable=False)  # contratado
    client_name = Column(String(200), nullable=False)  # contratante
    service_description = Column(Text, nullable=False)
    value = Column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    payment_terms = Column(String(255), nullable=False)
    city = Column(String(120), nullable=False)
    status = Column(String(50), nullable=False, default="rascunho")
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="contracts")
