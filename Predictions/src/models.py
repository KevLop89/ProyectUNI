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

def ResponseModel(data, message):
    return {
        "data": data,
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}
  


