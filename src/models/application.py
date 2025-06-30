from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum, ForeignKey
from src.db.base import Base
from enum import Enum
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .user import User


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[ApplicationStatus] = mapped_column(
        SQLEnum(ApplicationStatus), default=ApplicationStatus.PENDING
    )

    user: Mapped["User"] = relationship(back_populates="application")

    def __repr__(self):
        return f"<Application(id={self.id}, user_id={self.user_id}, status='{self.status}')>"

    def __str__(self):
        return f"Application {self.id} - User ID: {self.user_id} - Status: {self.status}"
