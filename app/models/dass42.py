from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base

class Dass42(Base):
    __tablename__ = "dass42"

    id = Column(Integer, primary_key=True, index=True)
    statement = Column(String)  # Pernyataan gejala / kuisioner
    category = Column(String) 

    # Menggunakan plural karena relasi ke Premise
    premises = relationship("Premise", back_populates="dass42")
