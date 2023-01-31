import pymysql
import os
global connection


def mysql_connect():
    
    try:
        os.environ['DEPLOYMENT']
        connection = pymysql.connect(
            host=os.environ["DBHOST"],
            user=os.environ['DBUSER'],
            passwd=os.environ['DBPASSWORD'],
            db=os.environ['DB'],
        )
        return connection
    except KeyError:
        from dotenv import load_dotenv
        load_dotenv()
        connection = pymysql.connect(
            host=os.getenv("DBHOST"),
            user=os.getenv('DBUSER'),
            passwd=os.getenv('DBPASSWORD'),
            db=os.getenv('DB'),
        )
        return connection
