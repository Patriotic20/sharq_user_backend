from sqlalchemy.orm import Mapped , mapped_column
from src.db.base import Base

class StudyInfo(Base):
    __tablename__ = "study_info"

    id: Mapped[int] = mapped_column(primary_key=True)
    study_language: Mapped[str] = mapped_column(nullable=False)
    study_form: Mapped[str] = mapped_column(nullable=False)
    study_direction: Mapped[str] = mapped_column(nullable=False)
    exam_form: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self):
        return (
            f"<StudyInfo(id={self.id}, language={self.study_language}, "
            f"form={self.study_form}, direction={self.study_direction}, "
            f"exam_form={self.exam_form})>"
        )

    def __str__(self):
        return (
            f"StudyInfo: Language={self.study_language}, Form={self.study_form}, "
            f"Direction={self.study_direction}, Exam Form={self.exam_form}"
        )
