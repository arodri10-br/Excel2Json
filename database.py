import mysql.connector
import configparser

def connect_db():
    config = configparser.ConfigParser()
    config.read('Excel2Json.ini')

    db_config = {
        'host': config['DATABASE']['host'],
        'user': config['DATABASE']['user'],
        'password': config['DATABASE']['password'],
        'database': config['DATABASE']['dbname']
    }

    conn = mysql.connector.connect(**db_config)
    return conn
