import pandas as pd
from .settings import *
from .redis_cache import *
import random
import string
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .auth.oauth2 import *


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def sql_current_date():
    now = datetime.utcnow()
    now.strftime('%Y-%m-%d %H:%M:%S')
    return now


def run_query(sql):
    try:
        connection = mysql_connect()
        """Runs a given SQL query via the global database connection.

        param sql: MySQL query
        return: Pandas dataframe containing results
        """
        result = pd.read_sql_query(sql, connection)

        result.replace({pd.NaT: None}, inplace=True)

        result.replace({np.nan: None}, inplace=True)

        return result
    except Exception as e:
        import traceback
        print(str(traceback.format_exc()), flush=True)
        connection.close()
        raise Exception('Error en base de datos')


def sql_insert(table: str, columnas: list, valores: list):
    try:
        connection = mysql_connect()
        cursor = connection.cursor()

        if len(columnas) != len(valores):
            raise Exception(
                "Los valores insertados deben ser iguales a las columnas")

        columns = ", ".join(columnas)

        values = '('
        for v in valores:
            values += '%s, '
        values += ')'
        values = values.replace(", )", ")")
        query = f"""
        INSERT INTO `{table}` ({columns})
        VALUES {values}
        """

        connection.ping()
        cursor.execute(query, valores)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        import traceback
        print(str(traceback.format_exc()), flush=True)
        connection.close()
        raise Exception('Error en base de datos')


def sql_update(table: str, columnas: list, valores: list, parametro: str, valor: str):
    try:
        connection = mysql_connect()
        cursor = connection.cursor()

        if len(columnas) != len(valores):
            raise Exception(
                "Los valores insertados deben ser iguales a las columnas")

        update = ''
        for c, v in zip(columnas, valores):
            update += f'{c} = "{v}", '
        update += ')'
        update = update.replace(", )", "").replace('None', 'NULL')
        update = update.replace('"NULL"', "NULL")
        print(update)
        query = f"""
        UPDATE `{table}`
        SET {update}
        WHERE {parametro} = '{valor}'
        """

        connection.ping()
        cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        import traceback
        print(str(traceback.format_exc()), flush=True)
        connection.close()


def sql_delete(table: str, parametro: str, valor: str):
    try:
        connection = mysql_connect()
        cursor = connection.cursor()

        query = f"""
        DELETE FROM `{table}`
        WHERE {parametro} = '{valor}'
        """

        connection.ping()
        cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        import traceback
        print(str(traceback.format_exc()), flush=True)
        connection.close()
        raise Exception('Error en base de datos')


def sql_search(table: str, parametro='id', valor='all', operator='=', order_by="", columns=[]):
    connection = mysql_connect()
    cursor = connection.cursor()

    if not order_by == "":
        order_by = "ORDER BY " + order_by
    try:
        if not columns:
            if valor == 'all':
                search = run_query(f"SELECT * FROM {table} {order_by}")
            else:
                search = run_query(
                    f"SELECT * FROM {table} WHERE {parametro} {operator} '{valor}' {order_by}")
        else:
            cols = ''
            for i in columns:
                cols += f'{i},'
            cols = cols[:-1]

            if valor == 'all':
                search = run_query(f"SELECT {cols} FROM {table} {order_by}")
            else:
                search = run_query(
                    f"SELECT {cols} FROM {table} WHERE {parametro} {operator} '{valor}' {order_by}")

    except Exception as e:
        search = pd.DataFrame()

    if search.empty:
        found = {}
    else:
        found = search.to_dict('records')

    return found


def sql_search_2_values(table: str,
                        parametro1: str,
                        valor1: str,
                        parametro2: str,
                        valor2: str,
                        operador1='=',
                        operador2='=',
                        order_by="",
                        columns=[],
                        ):
    connection = mysql_connect()
    cursor = connection.cursor()

    if not order_by == "":
        order_by = "ORDER BY " + order_by
    try:
        if not columns:
            search = run_query(f"SELECT * FROM {table} WHERE {parametro1} {operador1} "
                               f"'{valor1}' AND {parametro2} {operador2} '{valor2}' {order_by}")
        else:
            cols = ''
            for i in columns:
                cols += f'{i},'
            cols = cols[:-1]
            search = run_query(f"SELECT {cols} FROM {table} WHERE {parametro1} {operador1} "
                               f"'{valor1}' AND {parametro2} {operador2} '{valor2}' {order_by}")

    except Exception as e:
        search = pd.DataFrame()

    if search.empty:
        found = {}
    else:
        found = search.to_dict('records')

    return found


def sql_count(table: str):
    return int(run_query(f'SELECT COUNT(id) FROM {table};').to_dict('records')[0]['COUNT(id)'])


def sql_format_date_no_hour(date):
    try:
        formated_date = datetime.strptime(
            date, "%d/%m/%Y").strftime('%Y-%m-%d')
        formated_date = formated_date + " 00:00:00"
        return formated_date
    except:
        exception_date = '12/12/1971'
        formated_date = datetime.strptime(
            exception_date, "%d/%m/%Y").strftime('%Y-%m-%d')
        formated_date = formated_date + " 00:00:00"
        return formated_date


def generate_email_verification_token(email: str):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "email": email},
        expires_delta=access_token_expires
    )
    redis_tem_set(access_token, 60 * 60, access_token)
    return access_token


def send_email_password_recovery(url_link, to):
    # correos = [
    #     'victor.bonilla@easydata.com.co',
    #     'sebastian.rodriguez@easydata.com.co'
    # ]
    correos = [to]

    msg = MIMEMultipart()
    password = "gmeyyajithbcqthv"
    msg['Subject'] = "Confirmacion de correo"
    msg['From'] = "cowacolombia@gmail.com"
    msg['CCO'] = ", ".join(correos)
    """msg['To'] = destination_email """

    css = """
    <style>
    .container {
    background-color: white;
    color: black;
    }
    .card{
    display:flex;
    box-shadow: 0px 3px 6px #000000B3;
    width: 30%;
    border-radius:1vw;
    flex-direction: column;
    align-items: center;
    padding: 0 0vw;
    margin: 0 0 0 5vw;
    }
    .title{
    color: #113247;
    font-size: 2vw;
    font-weight: 900;
    margin: 1rem;
    }
    .text{
    font-size: 1vw;
    margin: 0 0 2rem;
    padding:  0 20%;
    }
    .link{
    background-color: #4AC4F0;
    color: white;
    text-decoration: none;
    width: 100%;
    text-align: center;
    font-size: 2vw;
    font-weight: 900;
    padding: 1rem 0;
    border-radius: 1vw
    }
    .image{
    width:100%;
    border-radius: 1vw;
    }
    </style>
    """
    msg.attach(MIMEText(f"""
    
    <div class="container">  
        <h1>Recupera tu contraseña de manera segura</h1>  
        <br>
        <h2>Verifica este correo y continua con el proceso de recuperación de contraseña.</h2>
        <br>
        <div class="card">
            <h3 class="text">
                Valida tu correo electrónico e inicia el cambio de tu contraseña
            </h3> 
            <br>
            <a class="link" href="{url_link}" target="_blank">
                Verificación del correo
            </a>
        </div>
    
    </div>


    """ + css, 'html'))

    server = smtplib.SMTP('smtp.gmail.com: 587')

    server.starttls()

    # Login Credentials for sending the mail
    server.login(msg['From'], password)

    # send the message via the server.
    server.sendmail(msg['From'], correos, msg.as_string())

    server.quit()


def xlsx_reader(file):
    try:
        size = 1000000
        data_xlsx = pd.read_excel(file)
        columns = list(data_xlsx.columns)
        values = data_xlsx.values.tolist()
        table = {
            "columns": columns,
            "data": values
        }
        return table
    except Exception as e:
        print(e)
