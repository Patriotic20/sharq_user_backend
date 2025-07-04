from pydantic import BaseModel , ConfigDict

class StudyFormBase(BaseModel):
    name: str

class StudyFormResponse(StudyFormBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class StudyFormFilter(BaseModel):
    name: str | None = None

class StudyFormUpdate(BaseModel):
    name: str | None = None


