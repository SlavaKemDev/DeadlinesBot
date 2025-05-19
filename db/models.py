from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, BigInteger
from .session import Base
from typing import Optional


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
