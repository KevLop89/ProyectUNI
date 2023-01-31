from cmath import pi
from pickle import TRUE
from fastapi import APIRouter
from fastapi import status as ResponseStatus
from fastapi import Request
from .auth.oauth2 import *
import traceback
from typing import Union
from fastapi import FastAPI, Header
from datetime import timedelta, datetime
import jwt

from .redis_cache import *
from .models import *
from .dependencies import *
from .settings import *

router = APIRouter()
from .swagger import *

import requests

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/", response_description="Health check")
async def healthcheck(request: Request, response: Response):
    return {"status": "ok"}


@router.post("/auth/oauth2", tags=['oauth'],response_description="Verifica usuario y contraseña y regresa un token")
async def oauth2(data: LoginData, response: Response):
    try:
        user = sql_search(table='users',parametro='email',valor=data.email)[0]
    except Exception as e:
        print(e)
        user = False

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(data.password, user['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "email": user['email'],
            "id": user['id']
        },
        expires_delta=access_token_expires
    )
    redis_tem_set(access_token, 60 * 60, access_token)

    return {
        "token": access_token,
        "id": user['id'],
        "msg": "Authentication OK",
        "status": "200"
    }

@router.post("/auth/create_user", response_description="Crea un usuario nuevo")
async def token_validation_external(data: LoginData, request: Request, response: Response):
    try:

        user = sql_search(table='users',parametro='email',valor=data.email)

        if len(user)>0:
            response.status_code = ResponseStatus.HTTP_409_CONFLICT
            return ErrorResponseModel(
                'Email already exist',
                code=409,
                message="Email already exist"
                )


        hashed_password = get_password_hash(data.password)

        sql_insert('users',['email','password'],[data.email,hashed_password])

        response_json = {"ok": True}

        return response_json
    except Exception as e:
        print(e)
        response.status_code = ResponseStatus.HTTP_500_INTERNAL_SERVER_ERROR
        import traceback
        return ErrorResponseModel(
            str(traceback.format_exc()),
            code=500,
            message="Error"
            )


@router.post("/auth/validation", response_description="Validacion JSON Web Token")
async def token_validation_external(data: Token, request: Request, response: Response):
    try:
        if not check_token(data.token) or data.token=='':
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return {"validation": False}

        response_json = {"validation": True}

        return response_json
    except Exception as e:
        response.status_code = ResponseStatus.HTTP_500_INTERNAL_SERVER_ERROR
        import traceback
        return ErrorResponseModel(
            str(traceback.format_exc()),
            code=500,
            message="Error"
            )


@router.get("/auth/email_check", response_description="Se verifica si el email esta registrado y confirmado")
async def email_check(email: str, request: Request, response: Response):
    try:
        try:
            user = sql_search(
                table='users',
                parametro='email',
                valor=email,
                columns=['email_confirmation']
            )[0]
        except KeyError():
            user = False

        if str(user['email_confirmation']):
            response.status_code = ResponseStatus.HTTP_409_CONFLICT
            return ResponseModel({"success": False}, "OK")

        return ResponseModel({"success": True}, "OK")
    except Exception as e:
        return ErrorResponseModel(str(e), code=500, message="Error")


@router.get("/auth/generate_token/{email}", response_description="Validacion JSON Web Token")
async def token_validation_external(request: Request,
                                    response: Response,
                                    email: str,
                                    reason: str = 'password_recovery'):
    """
    :param email: Email a donde se envia el URL con el token
    :param reason: La razon por la que se envia el token, donde el front sabe si es por un registro nuevo o por cambio
    de contraseña. Valores: ['email_confirmation', 'password_recovery']
    :return:
    """
    try:

        values = sql_search(
            table='users',
            parametro='email',
            valor=email,
            columns=['id']
        )

        if (not values):
            response.status_code = ResponseStatus.HTTP_409_CONFLICT
            return ErrorResponseModel(
                'Email not Found',
                code=409,
                message="Resource not exists"
                )
        else:
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={
                    "email": email
                },
                expires_delta=access_token_expires
            )
            redis_tem_set(access_token, 60 * 60, access_token)

            email_token = generate_email_verification_token(email)
            url_link = f'http://localhost:4200/login/new/{email_token}'
            send_email_password_recovery(url_link, email)
            return {
                "token": access_token,
                "url": url_link,
                "status": "200"
            }
    except Exception as e:
        print(e)
        response.status_code = ResponseStatus.HTTP_500_INTERNAL_SERVER_ERROR
        import traceback
        return ErrorResponseModel(
            str(traceback.format_exc()),
            code=500,
            message="Error"
            )


@router.post("/auth/update_user_password", response_description="Decodificar JSON Web Token para password")
async def edit_user_password(
        data: UserEditPassword,
        request: Request,
        response: Response,
):
    try:

        decoded = jwt.decode(data.token, SECRET_KEY, options={"verify_signature": False})
        decoded_email = decoded["email"]

        """
        Decodear el jwt y comprobar si el email existe
        """

        try:
            user = sql_search(table='users',parametro='email',valor=decoded_email)[0]
        except KeyError():
            user = False

        if not user:
            response.status_code = ResponseStatus.HTTP_404_NOT_FOUND
            return ErrorResponseModel(
                'Email not Found',
                code=409,
                message="Resource not found"
                )

        hashed_password = get_password_hash(data.new_password)

        """
        sql update con el parametro de email y la columna ['hashed_password'] valor [hashed_password]

        """
        sql_update(
            table='users',
            columnas=['password'],
            valores=[hashed_password],
            parametro='email',
            valor=decoded_email
        )

        return {'detail': 'Success'}

    except Exception as e:
        print(e)
        print(traceback.format_exc(), flush=True)
        return ErrorResponseModel(
            {'success': False},
            500,
            'Error'
        )
