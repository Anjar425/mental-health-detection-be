from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from ..database import Base


class AssessmentHistory(Base):
    __tablename__ = "assessment_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    depression_score = Column(Integer, nullable=True)
    anxiety_score = Column(Integer, nullable=True)
    stress_score = Column(Integer, nullable=True)

    type = Column(String, nullable=True)
    highest_severity = Column(String, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User")
