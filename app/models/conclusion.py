# models/conclusion.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Conclusion(Base):
    __tablename__ = "conclusions"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    severity_id = Column(Integer, ForeignKey("severity.id"))

    # Relasi
    category = relationship("Category", back_populates="conclusions")
    severity_data = relationship("Severity", back_populates="conclusions")

    rule = relationship("Rule", back_populates="conclusion", uselist=False)
