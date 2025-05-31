from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, BigInteger, ForeignKey, Integer, UniqueConstraint
from .session import Base
from typing import Optional, List
from datetime import datetime


class StudyProgram(Base):
    __tablename__ = "study_programs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))

    groups: Mapped[List["Group"]] = relationship(
        back_populates="study_program", cascade="all, delete-orphan"
    )

    users: Mapped[List["User"]] = relationship(
        back_populates="study_program", cascade="all, delete-orphan"
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    study_program_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("study_programs.id"), nullable=True)
    study_program = relationship("StudyProgram", back_populates="users")

    is_admin: Mapped[bool] = mapped_column(server_default='0', default=False)

    subscriptions: Mapped[List["UserSubscription"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))

    study_program_id: Mapped[int] = mapped_column(Integer, ForeignKey("study_programs.id"))
    study_program = relationship("StudyProgram", back_populates="groups")

    options: Mapped[List["GroupOption"]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )


class GroupOption(Base):
    __tablename__ = "group_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("groups.id"))
    name: Mapped[str] = mapped_column(String(50))
    telegram_channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    group: Mapped["Group"] = relationship(back_populates="options")
    subscribers: Mapped[List["UserSubscription"]] = relationship(
        back_populates="group_option", cascade="all, delete-orphan"
    )
    deadlines: Mapped[List["Deadline"]] = relationship(
        back_populates="group_option", cascade="all, delete-orphan"
    )


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    group_option_id: Mapped[int] = mapped_column(Integer, ForeignKey("group_options.id"))

    user: Mapped["User"] = relationship(back_populates="subscriptions")
    group_option: Mapped["GroupOption"] = relationship(back_populates="subscribers")


class Deadline(Base):
    __tablename__ = "deadlines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_option_id: Mapped[int] = mapped_column(Integer, ForeignKey("group_options.id"))
    name: Mapped[str] = mapped_column(String(150))
    date: Mapped[datetime] = mapped_column()

    group_option: Mapped["GroupOption"] = relationship(back_populates="deadlines")
    notifications: Mapped[List["Notification"]] = relationship(back_populates="deadline")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    deadline_id: Mapped[int] = mapped_column(Integer, ForeignKey("deadlines.id"))
    offset: Mapped[int] = mapped_column(Integer, default=0)

    deadline: Mapped["Deadline"] = relationship(back_populates="notifications")

    __table_args__ = (
        UniqueConstraint("deadline_id", "offset"),
    )
