from pydantic import BaseModel


class StudyInfoBase(BaseModel):
    study_language: str
    study_form: str
    study_direction: str
    exam_form: str


class StudyInfoCreate(StudyInfoBase):
    user_id: int


class StudyInfoResponse(StudyInfoCreate):
    id: int

class StudyInfoUpdate(BaseModel):
    study_language: str  | None = None
    study_form: str | None = None
    study_direction: str | None = None
    exam_form: str | None = None


class StudyInfoFilter(BaseModel):
    study_language: str  | None = None
    study_form: str | None = None
    study_direction: str | None = None
    exam_form: str | None = None
