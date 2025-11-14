from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Preference(Base):
    __tablename__ = "preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    dass21_id = Column(Integer, ForeignKey("dass21.id"))

    percent_anxiety = Column(Integer)
    percent_depression = Column(Integer)
    percent_stress = Column(Integer)

    # Relasi ke User
    user = relationship("User", back_populates="preferences")
    dass21 = relationship("Dass21", back_populates="preference")
