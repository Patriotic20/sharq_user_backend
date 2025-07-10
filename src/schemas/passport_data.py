from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional


class PassportDataBase(BaseModel):
    first_name: str
    last_name: str
    third_name: str
    date_of_birth: date
    passport_series_number: str
    jshshir: str
    issue_date: date
    gender: str


class PassportDataCreate(PassportDataBase):
    user_id: int
    passport_filepath: str


class PassportDataResponse(PassportDataBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class PassportDataUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    third_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    passport_series_number: Optional[str] = None
    jshshir: Optional[str] = None
    issue_date: Optional[date] = None
    gender: Optional[str] = None
