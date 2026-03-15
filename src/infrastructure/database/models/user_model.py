from sqlalchemy import Column, DateTime, String, UUID, func
from .base import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
