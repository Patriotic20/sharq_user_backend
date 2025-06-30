from sqlalchemy.orm import Mapped , mapped_column , relationship
from src.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .application import Application

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    phone_number: Mapped[str] = mapped_column(nullable=True)
    password: Mapped[str] = mapped_column(nullable=True)


    application: Mapped["Application"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, phone_number='{self.phone_number}')>"
    
    def __str__(self):
        return f"User {self.id} - Phone: {self.phone_number}"
