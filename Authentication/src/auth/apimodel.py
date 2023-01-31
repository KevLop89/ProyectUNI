from typing import List, Optional
from pydantic import BaseModel, Field


# Token return model
class Token(BaseModel):
    access_token: str = Field(..., example="YOUR_EASYBIO_ACCESS_TOKEN")
    token_type: str = Field(..., example='bearer')
    expire_minutes: int = Field(..., example=60)


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str = Field(..., example='my_user')
    email: Optional[str] = Field(None, example='myemail@example.com')
    full_name: Optional[str] = None
    role: str
    disabled: Optional[bool] = None
    route: Optional[str] = ''


class UserInDB(User):
    hashed_password: str

