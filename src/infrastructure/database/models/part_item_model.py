from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PartItemModel(Base):
    __tablename__ = "part_items"

    id = Column(UUID, primary_key=True)
    service_order_id = Column(
        UUID, ForeignKey("service_orders.id"), nullable=False
    )
    name = Column(String(255), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
