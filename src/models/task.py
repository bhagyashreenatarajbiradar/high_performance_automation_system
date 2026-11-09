
from sqlalchemy import Column, Integer, String, Text, Index

from src.database.database import Base


class Task(Base):
    __tablename__ = "tasks"

    __table_args__ = (
        Index("ix_tasks_status_priority", "status", "priority"),
    )

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False, index=True)

    description = Column(Text, nullable=True)

    status = Column(String(50), default="Pending", index=True)

    priority = Column(String(20), default="Medium")
