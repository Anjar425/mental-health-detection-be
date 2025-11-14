from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from ..database import Base
import enum

class RoleEnum(enum.Enum):
    user = "user"
    expert = "expert"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(RoleEnum), default=RoleEnum.user)

    rules = relationship("Rule", back_populates="user")
    profile = relationship("ExpertProfile", back_populates="user", uselist=False)
    weights = relationship("ExpertWeight", back_populates="user", uselist=False)
    preferences = relationship("Preference", back_populates="user")