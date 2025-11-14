# models/rule.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    conclusion_id = Column(Integer, ForeignKey("conclusions.id"))

    user = relationship("User", back_populates="rules")
    premises = relationship("Premise", back_populates="rule")
    conclusion = relationship("Conclusion", back_populates="rule", uselist=False)
