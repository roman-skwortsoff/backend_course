from pydantic import BaseModel, ConfigDict, EmailStr


class UserRequestAdd(BaseModel):
    email: EmailStr
    password: str


class UserAdd(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: int
    email: str

    model_config = ConfigDict(from_attributes=True)


class UseWithHashedPassword(User):
    password: str