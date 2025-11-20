from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base

class MemoryLog(Base):
    __tablename__ = "memory_log"

    id = Column(Integer, primary_key=True, index=True)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Plan(Base):
    __tablename__ = "plan"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    status = Column(String(50), default="created")
    created_at = Column(DateTime, default=datetime.utcnow)

    steps = relationship("Step", back_populates="plan", cascade="all, delete-orphan")


class Step(Base):
    __tablename__ = "step"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plan.id"), nullable=False)
    order = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="pending")
    result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    plan = relationship("Plan", back_populates="steps")