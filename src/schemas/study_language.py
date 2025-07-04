from pydantic import BaseModel , ConfigDict

class StudyLanguageBase(BaseModel):
    name: str

class StudyLanguageResponse(StudyLanguageBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class StudyLanguageFilter(BaseModel):
    name: str | None = None

class StudyLanguageUpdate(BaseModel):
    name: str | None = None


