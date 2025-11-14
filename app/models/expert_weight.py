from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class ExpertWeight(Base):
    __tablename__ = "expert_weights"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    education_weight = Column(Integer)
    patient_weight = Column(Integer)
    publication_weight = Column(Integer)
    flight_hours_weight = Column(Integer)

    user = relationship("User", back_populates="weights")
