from sqlalchemy import Column, Integer, String, Text, DateTime, func
from ..database import Base

class GroupWeight(Base):
    __tablename__ = "group_weights"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, unique=True, index=True)
    weights = Column(Text)  # JSON serialized vector
    signature = Column(String, nullable=True)
    meta = Column(Text, nullable=True)  # Optional JSON metadata about GA run
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
