from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from date_task_bot.schemas import ReminderStatus


class Base(DeclarativeBase):
    pass


class UserOrm(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    tasks: Mapped[TaskOrm] = relationship(cascade="all, delete-orphan", lazy="raise")

    def __init__(self, id: str):
        self.id = id


class TaskOrm(Base):
    __tablename__ = "tasks"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(
        ForeignKey(UserOrm.id, ondelete="CASCADE"), index=True
    )
    text: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    edited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    reminders: Mapped[RemindersOrm] = relationship(
        cascade="all, delete-orphan", lazy="raise"
    )

    def __init__(self, user_id: str, text: str):
        self.user_id = user_id
        self.text = text


class RemindersOrm(Base):
    __tablename__ = "reminders"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    task_id: Mapped[UUID] = mapped_column(
        ForeignKey(TaskOrm.id, ondelete="CASCADE"), index=True
    )
    remind_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    status: Mapped[ReminderStatus] = mapped_column(
        Enum(ReminderStatus, native_enum=True), default=ReminderStatus.PENDING
    )

    def __init__(self, task_id: UUID, remind_at: datetime):
        self.task_id = task_id
        self.remind_at = remind_at
