
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Index
)

from src.database.database import Base


class ExecutionHistory(Base):
    __tablename__ = "execution_history"

    __table_args__ = (
        Index("ix_execution_task_status", "task_id", "status"),
        Index("ix_execution_status_completed", "status", "completed_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, nullable=False, index=True)
    status = Column(String(50), default="Running", index=True)
    result = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


