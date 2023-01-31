from pydantic import BaseModel
from typing import Optional, Dict, List, Union


class Token(BaseModel):
    token: str

    class Config:
        schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                            "eyJ1aWQiOiI2Mjc4OGQ0ZWQ0YzY4ZDZkMDhlZTBhNTYiLCJuYW1lIjoiam9"
                            "yZ2U0IiwiaWF0IjoxNjUyMDY3NjYyLCJleHAiOjE2NTIxNTQwNjJ9.gTv_d"
                            "uJa3cTsq02CeTfjGGdr9Ysp8-cvDQw4mg-c24M",

            }
        }


class LoginData(BaseModel):
    email: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "easyClient@correo.com",
                "password": "easyPass",

            }
        }


class UserEditPassword(BaseModel):
    token: str
    new_password: str

    class Config:
        schema_extra = {
            "example": {
                "token": "token",
                "new_password": "easyPass2",
            }
        }


class Investor(BaseModel):
    name: str
    lastname: str
    doc_type: str
    doc_num: str
    password: str
    birth_date: Union[str, None]
    sex: str
    email: str
    cellphone: str
    # deactivated: int
    city_id: int
    state_id: int
    country_id: Union[int, None]=1
    token: str

    class Config:
        schema_extra = {
            "example": {
                "name": "string",
                "lastname": "string",
                "doc_type": "351351",
                "doc_num": "1615",
                "password": "string",
                "birth_date": "1971-12-12 00:00:00",
                "sex": "M",
                "email": "geo02134@gmail.com",
                "cellphone": "3223005270",
                "city_id": 169,
                "state_id": 4,
                "country_id": 1,
                "token": "prueba"
            }
        }


def ResponseModel(data, message):
    return {
        "data": data,
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}
  


