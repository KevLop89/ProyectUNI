from cmath import pi
from pickle import TRUE
from fastapi import APIRouter, FastAPI
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
from scipy import stats
from scipy.stats import boxcox
import random
import requests

from fastapi.middleware.cors import CORSMiddleware

class Data(BaseModel):
    columns: list
    data:list

def add_random_number(row):
    return row + np.random.uniform(0.00001, 0.00005)
                                   
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# appnn = FastAPI()
# origins = ["*"]
# appnn.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


@router.get("/", response_description="Health check")
async def healthcheck(request: Request, response: Response):
    return {"status": "kevin no es senior"}

#primera carga de datos y filtro 
@router.post("/predictions/excelToArray", response_description="Transforma el excel en array")
async def token_validation_external1(request: Request, response: Response, sheet_name: str, ingenieria: str, file: UploadFile = File(...)):
    #Carga inical de los datos y filtro de busqueda
    print("Si llego la peticion")
    try:
        iterador_i = 0
        datos_filtro = []
        initial_data = pd.read_excel(
            file.file.read(), sheet_name=sheet_name)
        initial_data = initial_data.fillna("None")
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
        print("Hola care bola")
        response.status_code = ResponseStatus.HTTP_500_INTERNAL_SERVER_ERROR
        import traceback
        return ErrorResponseModel(
            str(traceback.format_exc()),
            code=500,
            message="Error"
            )

#limpieza de los datos segun el fintro anterior
@router.post("/predictions/carga_limpieza", response_description="Limpia el archivo excel con el parametro tipo carrera")
async def token_validation_external2(response: Response,request: Request, data:Data):
    try:
        aux = pd.DataFrame(data.data, columns=data.columns)
        aux = aux.dropna(axis=1, how='all') 
        var_mayus=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','Ñ','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        var_min=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','ñ','o','p','q','r','s','t','u','v','w','x','y','z']
        aux = aux.replace('Á', 'A', regex=True).replace('É', 'E', regex=True).replace('Í','I', regex=True).replace('Ó','O', regex=True).replace('Ú','U', regex=True).replace('BOGOTÁ D.C', 'BOGOTA D.C.').replace('BOGOTA D.C', 'BOGOTA D.C.').replace('SANTAFE', 'SANTA FE').replace('RAFAEL URIBE', 'RAFAEL URIBE URIBE').replace("Ü", "U", regex=True).replace('a', 'A', regex=True).replace(var_min,var_mayus, regex=True).replace('Ã', 'A', regex=True).replace("NONE","None")
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

@router.post("/predictions/new_variables", response_description="Genera las nuevas variables a partir del excel")
# async def token_validation_external3(request: Request, response: Response,tipoCarrera: str, file: UploadFile = File(...)):
async def token_validation_external3(request: Request, response: Response, file: UploadFile = File(...)):
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

# trasposicion de la data -  PENDIENTES VARIABLES y semestre_asignatura
@router.post("/predictions/transform", response_description="Limpia el archivo excel sin parametros")
async def token_validation_external4(response: Response,data:Data, ingenieria:str, trans:str):
    try:
        
        aux = pd.DataFrame(data.data, columns=data.columns)
        num_var = ['biologia', 'quimica', 'fisica', 'sociales', 'aptitud_verbal', 'espanol_literatura', 'aptitud_matematica', 'condicion_matematica', 'filosofia', 'historia', 'geografia', 'idioma', 'interdiciplinar', 'codiogo_interdiciplinar', 
               'puntos_icfes', 'puntos_homologados']
        num_var += [col for col in aux if col.startswith('NOTA_SEM')] 
        num_var += [col for col in aux if col.startswith('VECES_SEM')]   

        aux[num_var] = aux[num_var].fillna(0).replace('None',0)
        print(aux)
        aux[num_var] = aux[num_var].astype(str).astype(float)
        var_const = [col for col in aux.select_dtypes(include=['float']) if aux[col].median()==aux[col].quantile(0.99)]
        aux[var_const] = aux[var_const].apply(add_random_number, axis = 1)

        
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
        # if semestre == False:
        #     aux = aux
        # else:
        #     #semestre = str(semestre)
        #     ##Pendiente obtener el dato 
        #     aux = aux[aux['semestre_asignatura'] == semestre]
        
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
                        elif trans == 'Box-Cox' and aux.shape[0] > 1:
                            aux[col] = aux[col] + 0.000000001
                            aux[col+'_'+trans], _ = boxcox(aux[col])
                            
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

#transpose Data
@router.post("/predictions/transpose", response_description="Limpia el archivo excel sin parametros")
async def transpose_initial_data(response: Response, data:Data, ingenieria:str ):

    try:

        df = pd.DataFrame(data.data, columns=data.columns)
        tr_df = df.loc[df['proyecto'] == ingenieria]
        tr_df['asignatura'] = tr_df['asignatura'].str.strip()
        tr_df['proyecto'] = tr_df['proyecto'].str.strip()
        
        tr_df['asignatura'] = tr_df['asignatura'].str.replace('\s+', ' ', regex=True)
        tr_df['proyecto'] = tr_df['proyecto'].str.replace('\s+', ' ', regex=True)

        
        
        aux = pd.read_excel('./Homologaciones_materia_agrupado.xlsx', sheet_name='limpieza')  #### relacionarlo con el excel que se carga en la homologación
        aux['asignatura'] = aux['asignatura'].str.strip()   
        aux['proyecto'] = aux['proyecto'].str.strip()   
        aux = aux[aux['proyecto'] == ingenieria] #### Este viene de las convenciones
        # aux = aux[aux['validacion'] == 'ok']  
        aux1 = aux[['proyecto','asignatura','asignatura_homologado']]
            
        tr_df = tr_df.merge(aux1, on = ['proyecto','asignatura'], how = 'left')
        tr_df['asignatura'] = np.where(tr_df['asignatura_homologado'].isnull(), tr_df.asignatura, tr_df.asignatura_homologado)
        
        tr_df['asignatura_homologado'] = np.where(tr_df['asignatura_homologado'].isnull(), tr_df.asignatura, tr_df.asignatura_homologado)
        
        # tr_df = tr_df.drop(columns = 'asignatura_homologado')
        
        aux2 = aux[['proyecto','asignatura_homologado','semestre','creditos','nucleo']]
        tr_df = tr_df.merge(aux2, on = ['proyecto','asignatura_homologado'], how = 'left')
        tr_df = tr_df[tr_df['creditos'].notna()]
        
        remove_colums = [
            "profundizacion",
            "valor_profundizacion",
            "profundizacion_dos",
            "valor_profundizacion_dos",
            "profundizacion_tres",
            "valor_profundizacion_tres"]

        tr_df.drop(remove_colums, axis=1, errors='ignore')
        
        if {"interdiciplinar", "codiogo_interdiciplinar"}.issubset(tr_df.columns) == True:
            tr_df["interdiciplinar"].fillna("NA", inplace=True)
            tr_df["codiogo_interdiciplinar"].fillna("NA", inplace=True)

            index_pivot = ["llave", "proyecto", "ano_ingreso", "semestre_ingreso", "metodologia", "modalidad", "nivel", "estrato",
                        "genero", "departamento", "municipio", "localidad", "tipo_colegio", "localidad_colegio",
                        "calendario_colegio", "municipio_colegio", "departamento_colegio", "inscripcion", "biologia", "quimica",
                        "fisica", "sociales", "aptitud_verbal", "espanol_literatura", "aptitud_matematica", "condicion_matematica",
                        "filosofia", "historia", "geografia", "idioma", "interdiciplinar", "codiogo_interdiciplinar", "puntos_icfes",
                        "puntos_homologados", "estado_actual"]
        else:

            index_pivot = ["llave", "proyecto", "ano_ingreso", "semestre_ingreso", "metodologia", "modalidad", "nivel", "estrato",
                        "genero", "departamento", "municipio", "localidad", "tipo_colegio", "localidad_colegio",
                        "calendario_colegio", "municipio_colegio", "departamento_colegio", "inscripcion", "biologia", "quimica",
                        "fisica", "sociales", "aptitud_verbal", "espanol_literatura", "aptitud_matematica", "condicion_matematica",
                        "filosofia", "historia", "geografia", "idioma", "puntos_icfes",
                        "puntos_homologados", "estado_actual"]

        tr_df['semestre'] = tr_df['semestre'].apply(str)
        tr_df['semestre'] = tr_df["semestre"].astype(
            str).apply(lambda x: x.replace('.0', ''))
        tr_df["asignatura_homologado"] = "SEM_" + \
            tr_df.semestre.str.cat(tr_df.asignatura_homologado, sep="-")
        
        transpose_df = np.round(tr_df.pivot_table(
            index=index_pivot, columns="asignatura_homologado", values="nota", aggfunc=['mean', "size"]), 2)

        transpose_df.columns = ["_".join(tup)
                                for tup in transpose_df.columns.to_flat_index()]

        transpose_df = transpose_df.reset_index()

        transpose_df.columns = [c.replace("mean", "NOTA")
                                for c in list(transpose_df.columns)]

        transpose_df.columns = [c.replace("size", "VECES")
                                for c in list(transpose_df.columns)]
        
        transpose_df2 = np.round(tr_df.pivot_table(
            index=index_pivot, columns="asignatura_homologado", values="creditos", aggfunc=['mean']), 2)
        
        transpose_df2.columns = ["_".join(tup)
                                for tup in transpose_df2.columns.to_flat_index()]

        transpose_df2 = transpose_df2.reset_index()

        transpose_df2.columns = [c.replace("mean", "CREDITOS")
                                for c in list(transpose_df2.columns)]
        transpose_df = transpose_df.merge(transpose_df2, how = 'left')
        # transpose_df.columns = transpose_df.columns.str.lower()

        # if write_table == "t":
        #     transpose_df.to_csv(path_output + "/transpose_df",
        #                         sep=";", encoding='utf8')
        transpose_df = transpose_df.fillna("None")
        print(transpose_df)
        columns = list(transpose_df.columns)
        values = transpose_df.values.tolist()
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
