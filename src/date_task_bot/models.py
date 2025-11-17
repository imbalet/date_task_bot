from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

from date_task_bot.schemas import ReminderStatus, TaskStatus

DEFAULT_OFFSETS = [
    timedelta(hours=0),
    timedelta(hours=-1),
    timedelta(hours=-2),
    timedelta(days=-1),
]


class RelativeTime(TypeDecorator):
    impl = INTERVAL
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(INTERVAL())
        else:
            return dialect.type_descriptor(Integer())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        else:
            return int(value.total_seconds())

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        else:
            return timedelta(seconds=value)


class Base(DeclarativeBase):
    pass


class UserOrm(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    tasks: Mapped[list[TaskOrm]] = relationship(
        cascade="all, delete-orphan", lazy="raise"
    )
    settings: Mapped[UserSettingsOrm] = relationship(
        cascade="all, delete-orphan", lazy="raise", uselist=False
    )

    def __init__(self, id: str, settings: UserSettingsOrm | None = None):
        self.id = id
        self.settings = settings or UserSettingsOrm()


class UserSettingsOrm(Base):
    __tablename__ = "user_settings"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(ForeignKey(UserOrm.id, ondelete="CASCADE"))
    timezone: Mapped[str] = mapped_column(default="UTC")

    timings: Mapped[list[DefaultRemindTimingOrm]] = relationship(
        cascade="all, delete-orphan", lazy="raise"
    )

    def __init__(
        self,
        timings: list[DefaultRemindTimingOrm] | None = None,
        user_id: str | None = None,
    ):
        self.timings = timings or [
            DefaultRemindTimingOrm(offset_seconds=t) for t in DEFAULT_OFFSETS
        ]
        if user_id:
            self.user_id = user_id


class DefaultRemindTimingOrm(Base):
    __tablename__ = "default_remind_timings"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    settings_id: Mapped[UUID] = mapped_column(
        ForeignKey(UserSettingsOrm.id, ondelete="CASCADE")
    )
    offset_seconds: Mapped[timedelta] = mapped_column(RelativeTime())

    __table_args__ = (
        UniqueConstraint("settings_id", "offset_seconds", name="uq_settings_timings"),
    )

    def __init__(self, offset_seconds: timedelta, settings_id: UUID | None = None):
        if settings_id:
            self.settings_id = settings_id
        self.offset_seconds = offset_seconds


class TaskOrm(Base):
    __tablename__ = "tasks"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(
        ForeignKey(UserOrm.id, ondelete="CASCADE"), index=True
    )
    text: Mapped[str]
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, native_enum=True), default=TaskStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    edited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    reminders: Mapped[list[ReminderOrm]] = relationship(
        cascade="all, delete-orphan", lazy="raise"
    )

    def __init__(
        self,
        user_id: str,
        text: str,
        due_date: datetime,
        reminders: list[ReminderOrm],
    ):
        self.user_id = user_id
        self.text = text
        self.due_date = due_date
        self.reminders = reminders


class ReminderOrm(Base):
    __tablename__ = "reminders"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    task_id: Mapped[UUID] = mapped_column(
        ForeignKey(TaskOrm.id, ondelete="CASCADE"), index=True
    )
    remind_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    offset_seconds: Mapped[timedelta] = mapped_column(RelativeTime())
    status: Mapped[ReminderStatus] = mapped_column(
        Enum(ReminderStatus, native_enum=True), default=ReminderStatus.PENDING
    )
    __table_args__ = (
        UniqueConstraint("task_id", "offset_seconds", name="uq_task_offset"),
    )

    def __init__(
        self,
        remind_at: datetime,
        offset_seconds: timedelta,
        task_id: UUID | None = None,
    ):
        if task_id:
            self.task_id = task_id
        self.remind_at = remind_at
        self.offset_seconds = offset_seconds
