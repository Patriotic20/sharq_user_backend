from src.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column , relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .study_info import StudyInfo

class StudyForm(Base):
    __tablename__ = "study_forms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    study_infos: Mapped[list["StudyInfo"]] = relationship(back_populates="study_form")


    def __repr__(self):
        return f"<StudyForm(id={self.id}, name='{self.name}')>"

    def __str__(self):
        return self.name
