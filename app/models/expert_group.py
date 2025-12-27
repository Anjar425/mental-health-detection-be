from sqlalchemy import Table, Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base

# Association table for many-to-many relationship
expert_group_association = Table(
    "expert_group_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("expert_groups.id"), primary_key=True),
)

class ExpertGroup(Base):
    __tablename__ = "expert_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    experts = relationship(
        "User",
        secondary=expert_group_association,
        back_populates="groups"
    )
