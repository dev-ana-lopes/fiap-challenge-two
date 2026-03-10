from sqlalchemy import Column, DateTime, String, UUID, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class CustomerModel(Base):
    __tablename__ = "customers"

    id = Column(UUID, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
