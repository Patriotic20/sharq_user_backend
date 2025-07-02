from pydantic import BaseModel


class StudyInfoBase(BaseModel):
    study_language: int
    study_form: int
    study_direction: int
    exam_form: int


class StudyInfoCreate(StudyInfoBase):
    user_id: int


class StudyInfoResponse(StudyInfoCreate):
    id: int

class StudyInfoUpdate(BaseModel):
    study_language: int  | None = None
    study_form: int | None = None
    study_direction: int | None = None
    exam_form: int | None = None


class StudyInfoFilter(BaseModel):
    study_language: int  | None = None
    study_form: int | None = None
    study_direction: int | None = None
    exam_form: int | None = None
