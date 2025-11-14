from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base

class Dass21(Base):
    __tablename__ = "dass21"

    id = Column(Integer, primary_key=True, index=True)
    statement = Column(String)
    category = Column(String)  

    preference = relationship("Preference", back_populates="dass21")

