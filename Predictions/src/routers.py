from cmath import pi
from pickle import TRUE
from fastapi import APIRouter
from fastapi import status as ResponseStatus
from fastapi import Request
from .auth.oauth2 import *
import traceback
from typing import Union
from fastapi import FastAPI, Header, UploadFile, File
from datetime import timedelta, datetime
import jwt

from .redis_cache import *
from .models import *
from .dependencies import *
from .settings import *
import pandas as pd 
import numpy as np
import json as json
router = APIRouter()
from .swagger import *
import sys
from pydantic import BaseModel
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

import requests
class Data(BaseModel):
    data:list

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/", response_description="Health check")
async def healthcheck(request: Request, response: Response):
    return {"status": "ok"}


@router.post("/predictions/excelToArray", response_description="Transforma el excel en array")
async def token_validation_external(request: Request, response: Response, sheet_name: str, ingenieria: str, file: UploadFile = File(...)):
    #Carga inical de los datos y filtro de busqueda
    try:
        iterador_i = 0
        datos_filtro = []
        initial_data = pd.read_excel(
            file.file.read(), sheet_name=sheet_name)

        columns = list(initial_data.columns)
        values = initial_data.values.tolist()
        table = {
            "columns": columns,
            "data": values
        }

        if ingenieria != 'TOTAL FACULTAD':
            #traer los datos solicitados segun el filtro de ingenieria
            for i in  table["data"]:
                if i[42] == ingenieria:
                    datos_filtro.append(table["data"][iterador_i])
                iterador_i += 1
                
            resultado = {
                "columns": columns,
                "data": datos_filtro
            }
            return resultado
        else:
            return table

    except Exception as e:
        response.status_code = ResponseStatus.HTTP_500_INTERNAL_SERVER_ERROR
        import traceback
        return ErrorResponseModel(
            str(traceback.format_exc()),
            code=500,
            message="Error"
            )

@router.post("/predictions/carga_limpieza", response_description="Limpia el archivo excel con el parametro tipo carrera")
async def token_validation_external(response: Response,request: Request, data:Data):
    try:
        datos = json.dumps(data.data)
        aux = pd.read_json(datos)
        aux = aux.dropna(axis=1, how='all')
        aux = aux.replace('Á', 'A', regex=True).replace('É', 'E', regex=True).replace('Í','I', regex=True).replace('Ó','O', regex=True).replace('Ú','U', regex=True).replace('BOGOTÁ D.C', 'BOGOTA D.C.').replace('BOGOTA D.C', 'BOGOTA D.C.').replace('SANTAFE', 'SANTA FE').replace('RAFAEL URIBE', 'RAFAEL URIBE URIBE').replace("Ü", "U", regex=True)
        values = aux.values.tolist()
        table = {
            "data": values
        }
        
        return table


    except Exception as e:
        response.status_code = ResponseStatus.HTTP_500_INTERNAL_SERVER_ERROR
        import traceback
        return ErrorResponseModel(
            str(traceback.format_exc()),
            code=500,
            message="Error"
            )

@router.post("/predictions/new_variables", response_description="Genera las nuevas variables a partir del excel")
async def token_validation_external(request: Request, response: Response,tipoCarrera: str, file: UploadFile = File(...)):
    try:
        
        if file.filename.endswith('.xlsx'):
            table = xlsx_reader(file.file.read())

        response_json = {"table": table}

        return response_json
    except Exception as e:
        response.status_code = ResponseStatus.HTTP_500_INTERNAL_SERVER_ERROR
        import traceback
        return ErrorResponseModel(
            str(traceback.format_exc()),
            code=500,
            message="Error"
            )

@router.post("/predictions/limpieza", response_description="Limpia el archivo excel sin parametros")
async def token_validation_external(request: Request, response: Response, file: UploadFile = File(...)):
    try:
        
        if file.filename.endswith('.xlsx'):
            table = xlsx_reader(file.file.read())

        response_json = {"table": table}

        return response_json
    except Exception as e:
        response.status_code = ResponseStatus.HTTP_500_INTERNAL_SERVER_ERROR
        import traceback
        return ErrorResponseModel(
            str(traceback.format_exc()),
            code=500,
            message="Error"
            )