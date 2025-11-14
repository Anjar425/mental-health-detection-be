from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from ..database import Base
import enum

class PrefixEnum(enum.Enum):
    no_prefix = "no_prefix"
    not_ = "not"

class ConjunctionEnum(enum.Enum):
    and_ = "and"
    or_ = "or"
    then = "then"

class LevelEnum(enum.Enum):
    low = "low"
    med = "med"
    high = "high"

class Premise(Base):
    __tablename__ = "premise"

    id = Column(Integer, primary_key=True, index=True)

    # Setiap premis terkait ke Question (gejala atau kuisioner)
    dass42_id = Column(Integer, ForeignKey("dass42.id"))

    # Setiap premis milik satu rule
    rule_id = Column(Integer, ForeignKey("rules.id"))

    # Menggunakan Enum untuk prefix, conjunction, dan level
    prefix = Column(Enum(PrefixEnum), default=PrefixEnum.no_prefix)  # no prefix / not
    conjunction = Column(Enum(ConjunctionEnum), default=ConjunctionEnum.and_)  # and / or / then
    level = Column(Enum(LevelEnum), default=LevelEnum.low)  # low / med / high

    # Relasi dengan Question dan Rule
    dass42 = relationship("Dass42", back_populates="premises")
    rule = relationship("Rule", back_populates="premises")
