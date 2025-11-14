from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class ExpertProfile(Base):
    __tablename__ = "expert_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    education_level = Column(String)
    publication_count = Column(Integer)
    patient_count = Column(Integer)
    flight_hours = Column(Integer)

    user = relationship("User", back_populates="profile")
