from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=24)


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=24)


class UserReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr

class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserReadSchema 