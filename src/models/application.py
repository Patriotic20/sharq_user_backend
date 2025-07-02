from src.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .exam_form import ExamForm
    from .study_form import StudyForm
    from .study_lenguage import StudyLanguage
    from .study_direction import StudyDirection
    from .user import User

class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    exam_form_id: Mapped[int] = mapped_column(ForeignKey("exam_forms.id"))
    study_direction_id: Mapped[int] = mapped_column(ForeignKey("study_directions.id"))
    study_form_id: Mapped[int] = mapped_column(ForeignKey("study_forms.id"))
    study_language_id: Mapped[int] = mapped_column(ForeignKey("study_languages.id"))

    # relationships
    user: Mapped["User"] = relationship(back_populates="application")
    exam_form: Mapped["ExamForm"] = relationship(back_populates="applications")
    study_direction: Mapped["StudyDirection"] = relationship(back_populates="applications")
    study_form: Mapped["StudyForm"] = relationship(back_populates="applications")
    study_language: Mapped["StudyLanguage"] = relationship(back_populates="applications")

    def __repr__(self):
        return (
            f"<Application(id={self.id}, user_id={self.user_id}, "
            f"exam_form_id={self.exam_form_id}, study_direction_id={self.study_direction_id}, "
            f"study_form_id={self.study_form_id}, study_language_id={self.study_language_id})>"
        )

    def __str__(self):
        return f"Application #{self.id} (User {self.user_id})"
