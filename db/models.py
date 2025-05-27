from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, BigInteger, ForeignKey, Integer
from .session import Base
from typing import Optional, List


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    subscriptions: Mapped[List["UserSubscription"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

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


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    group_option_id: Mapped[int] = mapped_column(Integer, ForeignKey("group_options.id"))

    user: Mapped["User"] = relationship(back_populates="subscriptions")
    group_option: Mapped["GroupOption"] = relationship(back_populates="subscribers")
