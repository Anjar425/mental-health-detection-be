# models/class.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base

class Severity(Base):
    __tablename__ = "severity"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

    conclusions = relationship("Conclusion", back_populates="severity_data")
