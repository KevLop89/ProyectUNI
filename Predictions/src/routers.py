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
from scipy import stats

import requests
class Data(BaseModel):
    columns: list
    data:list

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/", response_description="Health check")
async def healthcheck(request: Request, response: Response):
    return {"status": "ok"}

#primera carga de datos y filtro 
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

#limpieza de los datos segun el fintro anterior
@router.post("/predictions/carga_limpieza", response_description="Limpia el archivo excel con el parametro tipo carrera")
async def token_validation_external(response: Response,request: Request, data:Data):
    try:
        datos = json.dumps(data.data)
        aux = pd.read_json(datos)
        aux = aux.dropna(axis=1, how='all')
        aux = aux.replace('Á', 'A', regex=True).replace('É', 'E', regex=True).replace('Í','I', regex=True).replace('Ó','O', regex=True).replace('Ú','U', regex=True).replace('BOGOTÁ D.C', 'BOGOTA D.C.').replace('BOGOTA D.C', 'BOGOTA D.C.').replace('SANTAFE', 'SANTA FE').replace('RAFAEL URIBE', 'RAFAEL URIBE URIBE').replace("Ü", "U", regex=True)
        columns = data.columns
        values = aux.values.tolist()
        table = {
            "columns": columns,
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

# trasposicion de la data -  PENDIENTES BOX-COX y VARIABLES
@router.post("/predictions/transform", response_description="Limpia el archivo excel sin parametros")
async def token_validation_external(response: Response,data:Data, ingenieria:str,semestre:int, trans:str):
    try:
        
        aux = pd.DataFrame(data.data, columns=data.columns)
        num_var = ['biologia','quimica','fisica','sociales','aptitud_verbal','espanol_literatura','aptitud_matematica',
               'condicion_matematica','filosofia','historia','geografia','idioma','puntos_icfes',
               'puntos_homologados','nota','promedio']
    
        aux[num_var] = aux[num_var].astype(str).astype(float)
        opc_var = aux.columns
        trans = trans.split(',')
        # opc_tran_num = ['logaritmo','estandarizar','minmax','Box-Cox', 'Yeo-Johnson']
        opc_tran_num = trans

        #opc_tran_num = transformacion

        # validacion ingenieria
        if ingenieria == False:
            aux = aux
        else:
            aux = aux[aux['proyecto'] == ingenieria]
        # # validacion semestre
        if semestre == False:
            aux = aux
        else:
            #semestre = str(semestre)
            aux = aux[aux['semestre_asignatura'] == semestre]
        
        # # validacion variables (PENDIENTE)
        # # if var_sel == False:
        # #     aux = aux[opc_var]
        # # else:
        # #     aux = aux[var_sel]
        
        #aux = aux.reset_index().drop(columns = 'index')
        if aux.shape[0] > 0:
            for col in aux[num_var]:
                if aux[col].dtype == 'object':
                    print('La variable ' + col + ' es de tipo character/object. No puede ser transformada.')
                else:
                    for trans in opc_tran_num:
                        if trans == 'logaritmo':                       
                            aux[col+'_'+trans] = np.log10(aux[col])
                            if (aux[col].all() == False):
                                aux[col+'_'+trans] = 0.000000001
                        elif trans == 'estandarizar':
                            aux[col+'_'+trans] = (aux[col] - aux[col].values.mean()) / aux[col].values.std()
                            aux[col+'_'+trans].fillna('NaN', inplace=True)     
                        elif trans == 'minmax':
                            aux[col+'_'+trans] = (aux[col] - aux[col].values.min()) / aux[col].values.max()
                            aux[col+'_'+trans].fillna('NaN', inplace=True)
                        #PENDIENTE
                        elif trans == 'Box-Cox':
                            aux[col] = aux[col] + 0.000000001
                            aux[col+'_'+trans], _ = stats.boxcox(aux[col])
                        elif trans == 'Yeo-Johnson':
                            aux[col+'_'+trans], _ = stats.yeojohnson(aux[col])
                        else:              
                            print('No se ha encontrado una transformación adecuada. Seleccione una transformación')           
                    print('La variable ' + col + ' ha sido transformada bajo los siguientes criterios ' + str(opc_tran_num))
        
        columns = list(aux.columns)
        values = aux.values.tolist()
        table = {
            "columns": columns,
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