from sqlalchemy import Column, DateTime, ForeignKey, String, UUID, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ServiceOrderModel(Base):
    __tablename__ = "service_orders"

    id = Column(UUID, primary_key=True)
    customer_id = Column(UUID, ForeignKey("customers.id"), nullable=False)
    vehicle_id = Column(UUID, ForeignKey("vehicles.id"), nullable=False)
    status = Column(String(50), nullable=False, default="RECEIVED")
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
