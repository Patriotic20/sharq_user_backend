from pydantic import BaseModel , field_validator

class RegisterData(BaseModel):
    phone_number: str
    password:str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []

